import io
import logging
import os
import numpy as np
from modules import plugins, rife
import gradio as gr
from settings import HYPERTILE_VIDEO, TTS_VOICES_PATH
from submodules.hyper_tile.hyper_tile import split_attention
from utils.chat_utils import convert_gr_to_openai
from utils.file_utils import random_filename
from utils.gpu_utils import load_gpu_task
from utils.stable_diffusion_utils import inpaint_faces, upscale_with_img2img
from diffusers.utils import export_to_video
from PIL import Image
from apis.shape import generate_shape
from apis.musicgen import generate_music


chat_tts_settings = {
    "language": "en",
    "speed": 1,
    "temperature": 0.75,
    "voice": os.path.join(TTS_VOICES_PATH, "female1.wav"),
}


def set_language(value):
    chat_tts_settings["language"] = value


def set_speed(value):
    chat_tts_settings["speed"] = value


def set_temperature(value):
    chat_tts_settings["temperature"] = value


def set_voice(value):
    chat_tts_settings["voice"] = value


def play_wav_from_bytes(wav_bytes):

    import pygame

    pygame.mixer.init()
    sound = pygame.mixer.Sound(io.BytesIO(wav_bytes))
    sound.play()

    # Wait for the sound to finish playing
    pygame.time.wait(int(sound.get_length() * 1000))


async def chat(text: str, history: list[list], speak_results: bool, chunk_sentences):
    from clients import TTSClient
    from apis.llm import chat, chat_streaming

    message = ""
    if not speak_results:
        async for chunk in chat_streaming(
            text=text,
            messages=convert_gr_to_openai(history),
        ):
            message += chunk
            yield message, None
        return

    response = await chat(
        text=text,
        messages=convert_gr_to_openai(history),
    )

    logging.info("\nGenerating speech...")

    audio = await TTSClient.generate_speech(
        response,
        speed=chat_tts_settings["speed"],
        temperature=chat_tts_settings["temperature"],
        speaker_wav=chat_tts_settings["voice"],
        language=chat_tts_settings["language"],
    )
    play_wav_from_bytes(audio)

    yield response


def preview_speech(
    text: str,
    speed: int,
    temperature: float,
    top_p: float,
    voice: str,
    language: str,
):
    from clients import TTSClient

    for chunk in TTSClient.generate_speech_streaming(
        text,
        speed=speed,
        temperature=temperature,
        top_p=top_p,
        speaker_wav=voice,
        language=language,
    ):
        yield (24000, chunk)


async def generate_video(
    image_input,
    width: int,
    height: int,
    num_inference_steps: int,
    fps: int,
    motion_bucket_id: int,
    noise: float,
    interpolate: int,
    num_frames: int,
    decode_chunk_size: int,
):
    yield gr.Video(), gr.Button("Generating...", interactive=False)

    # Convert numpy array to PIL Image
    pipe = await load_gpu_task("img2vid", plugins.image_pipelines["img2vid"])

    image = Image.fromarray(image_input).convert("RGB")
    filename_noext = random_filename()

    def do_gen():
        video_frames = pipe(
            image,
            num_inference_steps=num_inference_steps,
            num_frames=num_frames,
            motion_bucket_id=motion_bucket_id,
            decode_chunk_size=decode_chunk_size,
            width=width,
            height=height,
            noise_aug_strength=noise,
        ).frames[0]

        if interpolate > 1:
            video_frames = rife.interpolate(
                video_frames,
                count=interpolate,
                scale=1,
                pad=1,
                change=0,
            )
            export_to_video(
                video_frames,
                f"{filename_noext}.mp4",
                fps=fps * interpolate,
            )

        else:
            export_to_video(video_frames, f"{filename_noext}.mp4", fps=fps)

        return f"{filename_noext}.mp4", gr.Button("Generate Video", interactive=True)

    if HYPERTILE_VIDEO:
        aspect_ratio = 1 if width == height else width / height
        split_vae = split_attention(
            plugins.image_pipelines["img2vid"].vae,
            tile_size=256,
            aspect_ratio=aspect_ratio,
        )
        split_unet = split_attention(
            plugins.image_pipelines["img2vid"].unet,
            tile_size=256,
            aspect_ratio=aspect_ratio,
        )
        with split_vae:
            with split_unet:
                yield do_gen()

    else:
        yield do_gen()


async def txt2img(
    model: str,
    prompt: str,
    negative_prompt: str,
    width: int,
    height: int,
    num_inference_steps: int,
    guidance_scale: float,
    fix_faces: bool,
    upscale: bool,
    upscale_ratio: float,
):    
    txt2img = plugins.get_resource(
        plugins.SupportedPipelines.STABLE_DIFFUSION, "txt2img"
    )

    kwargs = dict(
        prompt=prompt,
        negative_prompt=negative_prompt,
        num_inference_steps=num_inference_steps,
        guidance_scale=guidance_scale,
        width=width,
        height=height,
    )
    image = txt2img(**kwargs).images[0]

    if upscale is True:
        image = upscale_with_img2img(
            image,
            prompt=prompt,
            negative_prompt=negative_prompt,
            original_width=width,
            original_height=height,
            upscale_coef=upscale_ratio,
            num_inference_steps=num_inference_steps,
        )

    if fix_faces is True:
        image = inpaint_faces(image, **kwargs)

    yield image, gr.Button(label="Generate Video", interactive=True)


async def audiogen(prompt: str, duration: float, temperature: float):
    from clients import AudioGenClient

    filename_noext = random_filename()
    return await AudioGenClient.generate(
        prompt,
        file_path=filename_noext,
        duration=duration,
        temperature=temperature,
    )


async def musicgen(
    prompt: str,
    duration: float,
    temperature: float,
    guidance_scale: float,
    top_p: float,
):
    result = generate_music(
        prompt=prompt,
        duration=duration,
        temperature=temperature,
        guidance_scale=guidance_scale,
        top_p=top_p,
        format="wav",
        streaming=True,
    )
    print(result)
    i = 0
    chunks = []
    async for sample_rate, chunk in result:
        i = i + 1
        chunks.append(chunk)
        if i < 3:
            print("Buffering...")
        elif i == 3:
            yield (sample_rate, np.concatenate(chunks)), None, None
        else:
            yield (sample_rate, chunk), None, None

    full_wav = (32000, np.concatenate(chunks))

    yield None, full_wav, gr.make_waveform(full_wav)


async def shape_generate(prompt: str, num_inference_steps: int, guidance: float):
    file_path_noext = random_filename()
    file_path = await generate_shape(
        prompt,
        file_path_noext=file_path_noext,
        num_inference_steps=num_inference_steps,
        guidance_scale=guidance,
        format="glb",
    )
    yield file_path


def disable_send_button():
    yield gr.Button(label="Generating...", interactive=False)
