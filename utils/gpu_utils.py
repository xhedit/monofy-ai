import gc
import asyncio
import logging
import time
import torch
import numpy as np


idle_offload_time = 120

torch.set_grad_enabled(False)
if torch.cuda.is_available():
    torch.backends.cudnn.enabled = True
    torch.backends.cudnn.benchmark = True


def set_idle_offload_time(timeout_seconds: float):
    global idle_offload_time
    idle_offload_time = timeout_seconds


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


def load_gpu_task(task_name: str, client, free_vram=True):
    if not torch.cuda.is_available():
        return

    global current_tasks
    global last_task

    last_used[task_name] = time.time()
    last_task = task_name

    if task_name == last_task or not free_vram:
        return

    before = torch.cuda.memory_reserved()

    if free_vram:
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

    if empty_cache:
        torch.cuda.empty_cache()
        gc.collect()
        after = torch.cuda.memory_reserved()
        gib = bytes_to_gib(before - after)
        if gib > 0:
            logging.info(f"Freed {gib:.2f} GiB from VRAM cache")

        logging.warn(f"Loading {task_name}...")

    last_used[task_name] = time.time()


def free_idle_vram(for_task: str):

    t = time.time()
    for name, client in current_tasks.items():
        #if not (name in chat_tasks and for_task in chat_tasks):
        elapsed = t - last_used[name]
        if elapsed > idle_offload_time:
            logging.info(
                f"{name} was last used {round(elapsed,2)} seconds ago."
            )
            logging.info(f"Offloading {name} (idle)...")
            client.offload(for_task)
