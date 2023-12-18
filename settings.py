import logging
import sys

print("Python version:", sys.version)

LOG_LEVEL = logging.INFO

# Disable on non-cuda devices
USE_XFORMERS = True
USE_CUDAGRAPH = True
USE_ACCELERATE = True

# Support for microsoft/DeepSpeed
# install manually in the venv before enabling (good luck on Windows)
USE_DEEPSPEED = False

# FastAPI
HOST = "127.0.0.1"
PORT = 5000

TTS_VOICES_PATH = "voices"
MEDIA_CACHE_DIR = ".cache"

# THIS BOT HAS ONLY BEEN TESTED WITH THESE MODELS
# For LLM, any exl2 model will work but may require adjusting settings
# For TTS, stick to XTTS-v2 or use --edge-tts
LLM_MODEL = "LoneStriker/dolphin-2.2.1-mistral-7b-4.0bpw-h6-exl2"  # hf model tag
# LLM_MODEL = "TheBloke/Orca-2-7B-GPTQ" # experimental
TTS_MODEL = "coqui/XTTS-v2"  # hf model tag

SD_MODEL = "models/sd/realisticVisionV51_v51VAE.safetensors"
# SD_MODEL = "models/sd/jernaumix_chimeraV30.safetensors"
# SD_MODEL = "models/sdxl/pixelwaveturbo_01.safetensors" # be sure to set SD_USE_SDXL = True
# SD_MODEL = "stabilityai/sdxl-turbo" # TODO this line is a placeholder, still need to support loading hf tags
SD_USE_SDXL = False  # Set to True for SDXL/turbo models
SD_DEFAULT_STEPS = 25  # Set to 20-40 for non turbo models, or 6-10 for turbo
SD_DEFAULT_GUIDANCE_SCALE = 3.0  # If guidance_scale is not provided (default = 3.0)
SD_USE_VAE = True  # Load ConsistencyDecoderVAE using model config
SD_IMAGE_WIDTH = 512
SD_IMAGE_HEIGHT = 512

LLM_DEFAULT_SEED = 42  # Use -1 for a random seed on each reply (recommended)
LLM_GPU_SPLIT = (
    None  # [4000]  # Split between multiple GPUs, increase if using a larger model
)
LLM_MAX_SEQ_LEN = 4096  # Sequence length (default = 2048 but you can go higher)
LLM_SCALE_POS_EMB = (
    1.5  # (recommended = 2.0 @ 4096) 1.0 works great but generates lengthy replies
)

# These values are what appear in chat logs which the model is "completing" on each request
# OpenAI message format will be converted to "Name: message\n\n" and dumped as a single message
LLM_DEFAULT_USER = "User"
LLM_DEFAULT_ASSISTANT = "Assistant"

# Used when determining if a response was cut off
# When chunking by sentences, this can cause emojis at the end to be truncated
# Who cares, though? Plus once they end with an emoji they constant keep doing it
LLM_VALID_ENDINGS = [".", "?", "!", "}", "```"]

# These values are added in addition to the model's built-in eos_token_id value
# No exact science implemented here so feel free to adjust as needed
LLM_STOP_CONDITIONS = [
    "\n\n--",
    "\n\n##",
    f"\n\n{LLM_DEFAULT_USER}:",
    f"\r{LLM_DEFAULT_USER}:",
    f"\n{LLM_DEFAULT_USER}:",
    f"\n\n{LLM_DEFAULT_ASSISTANT}:",
    f"\r{LLM_DEFAULT_ASSISTANT}:",
    f"\n{LLM_DEFAULT_ASSISTANT}:",
    "[img]",
    "(This response",
    "\nRemember, ",
]
