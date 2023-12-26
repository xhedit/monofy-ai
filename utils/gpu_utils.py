import gc
import asyncio
import logging
import time
from fastapi import BackgroundTasks
import torch
import numpy as np


idle_offload_time = 120

def set_idle_offload_time(timeout_seconds: float):
    global idle_offload_time
    idle_offload_time = timeout_seconds

logging.basicConfig(level=logging.INFO)

gpu_thread_lock = asyncio.Lock()


def autodetect_device():
    """Returns a device such as "cpu" or "cuda:0" """
    return torch.device("cuda:0" if torch.cuda.is_available() else "cpu")


def get_seed(seed: int = -1):
    # Check if CUDA is available
    if torch.cuda.is_available():
        # Use CUDA random number generator
        generator = torch.cuda.random.seed() if -1 else torch.cuda.manual_seed(seed)
    else:
        # Use CPU random number generator
        generator = torch.manual_seed(seed)

    return generator


def bytes_to_gib(bytes_value):
    gib_value = bytes_value / (1024**3)
    return gib_value


def fp16_available():
    try:
        # Attempt to create a NumPy array with dtype=float16
        np.array(1, dtype=np.float16)
        return True
    except TypeError:
        return False


current_tasks = {}
last_used = {}
last_task = None
small_tasks = ["exllamav2", "tts", "stable diffusion"]
large_tasks = ["sdxl", "svd", "shap-e", "audiogen", "musicgen"]
chat_tasks = ["exllamav2", "tts", "whisper"]

def free_vram(task_name: str, client):

    if not torch.cuda.is_available():
        return
    
    global current_tasks
    global last_task
    
    before = torch.cuda.memory_reserved()        

    free_idle_vram(task_name)

    small_tasks_only = last_task is not None and last_task in small_tasks

    empty_cache = task_name != last_task

    if small_tasks_only:
        if task_name in large_tasks:
            empty_cache = True
            for _, client in current_tasks.items():
                client.offload(task_name)
            current_tasks.clear()
    else:
        if current_tasks:
            empty_cache = True
            for _, client in current_tasks.items():
                client.offload(task_name)
            current_tasks.clear()

    current_tasks[task_name] = client
    last_task = task_name

    if empty_cache:        
        torch.cuda.empty_cache()
        gc.collect()
        after = torch.cuda.memory_reserved()
        gib = bytes_to_gib(before - after)
        if gib > 0:
            logging.info(f"Freed {round(gib,2)} GiB from VRAM cache")        

        logging.info(f"Loading {task_name}...")

    

    last_used[task_name] = time.time()

vram_monitor_started = False

# currently unused
async def vram_monitor(background_tasks: BackgroundTasks):
    if not vram_monitor_started:            
        logging.info("VRAM monitor started.")
        while True:
            background_tasks.add_task(free_idle_vram)
            await asyncio.sleep(idle_offload_time)

def free_idle_vram(for_task: str):
    if for_task != last_task:
        logging.info("Checking idle times...")
        t = time.time()
        for name, client in current_tasks.items():
            if not (name in chat_tasks and for_task in chat_tasks):
                elapsed = t - last_used[name]
                logging.info(f"{name} was last used {elapsed} seconds ago.")
                if elapsed > 30:
                    logging.info(f"Offloading {name} (idle)...")
                    client.offload(for_task)
