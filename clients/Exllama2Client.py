from typing import Generator
import re
import logging
from utils.gpu_utils import load_gpu_task
from utils.text_utils import process_text_for_llm
from huggingface_hub import snapshot_download
from settings import (
    DEVICE,
    LLM_MAX_NEW_TOKENS,
    LLM_MODEL,
    LLM_DEFAULT_SEED,
    LLM_GPU_SPLIT,
    LLM_MAX_SEQ_LEN,
    LLM_SCALE_POS_EMB,
    LLM_STOP_CONDITIONS,
    LLM_VALID_ENDINGS,
)
import time
import os
from typing import List
from exllamav2 import (
    ExLlamaV2,
    ExLlamaV2Config,
    ExLlamaV2Cache,
    ExLlamaV2Tokenizer,
)
from exllamav2.generator import (
    ExLlamaV2BaseGenerator,
    ExLlamaV2StreamingGenerator,
    ExLlamaV2Sampler,
)
from clients import Exllama2Client


friendly_name = "exllamav2"
logging.warn(f"Initializing {friendly_name}...")
current_model_name = LLM_MODEL
model_path = None
model = None
config = None
cache = None
tokenizer = None
generator = None
streaming_generator = None
user_name = "User"
assistant_name = "Assistant"
context = f"Considering the following conversation between {user_name} and {assistant_name}, give a single response as {assistant_name}. Do not prefix with your own name. Do not prefix with emojis."


def load_model(model_name=current_model_name):
    global current_model_name
    global model
    global tokenizer
    global cache
    global generator
    global streaming_generator

    if model and model_name == model_name:
        return

    path = "models/llm/models--" + model_name.replace("/", "--")
    if os.path.isdir(path):
        model_path = os.path.abspath(path)
    else:
        model_path = snapshot_download(
            repo_id=LLM_MODEL, cache_dir="models/llm", local_dir=path
        )
    
    config = ExLlamaV2Config()
    config.model_dir = model_path
    config.prepare()
    config.max_seq_len = LLM_MAX_SEQ_LEN
    config.scale_pos_emb = LLM_SCALE_POS_EMB
    # config.set_low_mem = True

    if model:
        logging.warn(f"Unloading {current_model_name} model...")
        model.unload()
        del model

    current_model_name = model

    model = ExLlamaV2(config, lazy_load=True)
    logging.warn("Loading model: " + model_name)

    cache = ExLlamaV2Cache(model, lazy=True)
    model.load_autosplit(cache, LLM_GPU_SPLIT)

    tokenizer = ExLlamaV2Tokenizer(config)
    generator = ExLlamaV2BaseGenerator(model, cache, tokenizer)

    streaming_generator = ExLlamaV2StreamingGenerator(model, cache, tokenizer)

    stop_conditions = [tokenizer.eos_token_id] + LLM_STOP_CONDITIONS
    streaming_generator.set_stop_conditions(stop_conditions)


def unload():
    global model
    global cache
    global tokenizer
    if model is not None:
        logging.warn(f"Unloading {friendly_name}...")
        model.unload()
        del cache
        del model
        del tokenizer
        cache = None
        model = None
        tokenizer = None


def offload(for_task: str):
    logging.warn(f"No offload available for {friendly_name}.")
    unload()


def refresh_context(from_api: bool = False):
    global context
    try:
        with open("context.txt", "r") as file:
            context = file.read()
            if from_api:
                logging.warn("Refreshed settings via API request.")
    except Exception:
        logging.error("Error reading context.txt, using default.")


def generate_text(
    prompt: str,
    max_new_tokens: int = LLM_MAX_NEW_TOKENS,
    temperature: float = 0.7,
    top_p=0.9,
    chunk_sentences: bool = False,
    token_repetition_penalty=1.15,
    seed=LLM_DEFAULT_SEED,
) -> Generator[str, None, None]:
    load_gpu_task(friendly_name, Exllama2Client)

    if model is None:
        load_model()

    settings = ExLlamaV2Sampler.Settings()
    settings.temperature = temperature
    settings.top_k = 20
    settings.top_p = top_p
    settings.token_repetition_penalty = 1.15
    settings.typical = 1.0

    if tokenizer is None:
        raise Exception("tokenizer is NoneType")
    settings.disallow_tokens(tokenizer, [tokenizer.eos_token_id])

    time_begin = time.time()

    # print(f"\nFull text:\n---\n{prompt}\n---\n")

    generated_tokens = 0

    logging.info("Streaming response...")

    input_ids = tokenizer.encode(prompt)
    input_ids.to(DEVICE)

    streaming_generator.warmup()
    streaming_generator.begin_stream(input_ids, settings, True)

    message = ""
    sentence_count = 0
    i = 0

    while True:
        i += 1
        if i > LLM_MAX_SEQ_LEN:
            break  # *probably* impossible

        chunk, eos, _ = streaming_generator.stream()
        generated_tokens += 1

        # Never start a sentence with an emoji.
        # This quickly results in *every* sentence starting with an emoji.
        if message == "":
            chunk = process_text_for_llm(chunk)

        message += chunk

        if chunk_sentences:
            # Check if there's a complete sentence in the message
            if any(punctuation in message for punctuation in [".", "?", "!"]):
                # Split the message into sentences and yield each sentence
                sentences = re.split(r"(?<=[.!?])\s+", message)
                for sentence in sentences[:-1]:
                    yield (" " if sentence_count > 0 else "") + process_text_for_llm(
                        sentence
                    )
                    sentence_count += 1
                message = sentences[
                    -1
                ]  # Keep the incomplete sentence for the next iteration

        else:
            yield process_text_for_llm(chunk)

        if eos or generated_tokens == max_new_tokens:
            break

    if (
        chunk_sentences
        and message
        and (message[-1] in LLM_VALID_ENDINGS)
        or message[-3:] == "```"
    ):
        yield (" " if sentence_count > 0 else "") + process_text_for_llm(message)

    del input_ids

    time_end = time.time()
    time_total = time_end - time_begin

    print()
    print(
        f"Response generated in {time_total:.2f} seconds, {generated_tokens} tokens, {generated_tokens / time_total:.2f} tokens/second"
    )


def chat(
    text: str,
    messages: List[dict],
    context="",
    max_new_tokens=80,
    temperature=0.7,
    top_p=0.9,
    chunk_sentences=True,
):
    prompt = (
        "System: " + (context + "\n\n" + context + "\n") if context else f"{context}\n"
    )

    for message in messages:
        role = message.get("role", "")
        content = message.get("content", "")
        name = user_name if role == "user" else assistant_name
        prompt += f"\n\n{name}: {content}"

    if text is not None:
        prompt += f"\n\n{user_name}: {text}"

    prompt += f"\n\n{assistant_name}: "

    return generate_text(
        prompt=prompt,
        max_new_tokens=max_new_tokens,
        temperature=temperature,
        top_p=top_p,
        chunk_sentences=chunk_sentences,
    )


refresh_context()
