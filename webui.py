import logging
import io
import torch
from clients.llm.Exllama2Client import Exllama2Client
from clients.llm.chat_utils import convert_gr_to_openai
from clients.sd.SDClient import SDClient
from settings import LOG_LEVEL
from ttsclient import TTSClient
from utils.torch_utils import autodetect_device
import gradio as gr

logging.basicConfig(level=LOG_LEVEL)

device = autodetect_device()

settings = {
    "language": "en",
    "speed": 1,
    "temperature": 0.75,
    "voice": "voices/female1.wav",
}


def launch_webui(use_llm=False, use_tts=False, use_sd=False, prevent_thread_lock=False):
    tts: TTSClient = None
    llm: Exllama2Client = None

    if use_tts:
        tts = TTSClient.instance

    if use_llm:
        llm = Exllama2Client.instance

    with gr.Blocks(title="monofy-ai", analytics_enabled=False) as web_ui:
        if use_llm:
            with gr.Tab("LLM"):
                grChatSpeak = None

                async def chat(text: str, history: list[list], chunk_sentences=True):
                    print(f"text={text}")
                    print(f"chunk_sentences={chunk_sentences}")

                    response = llm.chat(
                        text=text,
                        messages=convert_gr_to_openai(history),
                        chunk_sentences=chunk_sentences,
                    )

                    message = ""
                    for chunk in response:
                        if chunk_sentences:
                            message += " " + chunk

                            if tts and grChatSpeak.value:
                                print("")
                                logging.info("\nGenerating speech...")

                                audio = tts.generate_speech(
                                    chunk,
                                    speed=settings["speed"],
                                    temperature=settings["temperature"],
                                    speaker_wav=settings["voice"],
                                    language=settings["language"],
                                )
                                yield message.strip()
                                play_wav_from_bytes(audio)

                        else:
                            message += chunk
                            yield message

                with gr.Column():
                    with gr.Row():
                        grChatSentences = gr.Checkbox(
                            value=True, label="Chunk full sentences"
                        )
                        grChatSpeak = gr.Checkbox(
                            value=use_tts,
                            interactive=use_tts,
                            label="Speak results",
                        )
                    gr.ChatInterface(
                        fn=chat, additional_inputs=[grChatSentences]
                    ).queue()

        if use_tts:
            with gr.Tab("TTS"):
                import simpleaudio as sa

                def play_wav_from_bytes(wav_bytes):
                    wave_obj = sa.WaveObject.from_wave_file(io.BytesIO(wav_bytes))
                    play_obj = wave_obj.play()

                    # Wait for the sound to finish playing
                    play_obj.wait_done()

                def set_language(value):
                    settings["language"] = value

                def set_speed(value):
                    settings["speed"] = value

                def set_temperature(value):
                    settings["temperature"] = value

                def set_voice(value):
                    settings["voice"] = value

                with gr.Column():
                    grText = gr.Textbox(
                        "This is a test of natural speech.", label="Text"
                    )
                    grVoice = gr.Textbox("voices/female1.wav", label="Voice")
                    with gr.Row():
                        grSpeed = gr.Number("1", label="Speed")
                        grTemperature = gr.Number("0.75", label="Temperature")

                        grLanguage = gr.Dropdown(
                            [
                                "en",
                                "es",
                                "fr",
                                "de",
                                "it",
                                "pt",
                                "pl",
                                "tr",
                                "ru",
                                "nl",
                                "cs",
                                "ar",
                                "zh-cn",
                                "ja",
                                "hu",
                                "ko",
                            ],
                            label="Language",
                            value=settings["language"],
                        )
                    grLanguage.change(set_language, inputs=[grLanguage])
                    grSpeed.change(set_speed, inputs=[grSpeed])
                    grTemperature.change(set_temperature, inputs=[grTemperature])
                    grVoice.change(set_voice, inputs=[grVoice])
                    grGenerateButton = gr.Button("Generate")
                    grAudioOutput = gr.Audio(
                        label="Audio Output",
                        type="numpy",
                        autoplay=True,
                        format="wav",
                        streaming=False,  # TODO
                    )

                    async def preview_speech(
                        text: str,
                        speed: int,
                        temperature: float,
                        voice: str,
                        language: str,
                    ):
                        # TODO stream to grAudio using generate_text_streaming
                        speech = tts.generate_speech(
                            text,
                            speed,
                            temperature,
                            voice,
                            language,
                        )
                        yield speech

                    grGenerateButton.click(
                        preview_speech,
                        inputs=[grText, grSpeed, grTemperature, grVoice, grLanguage],
                        outputs=[grAudioOutput],
                    )

                # Right half of the screen (Chat UI) - Only if use_llm is True

        if use_sd:
            sd = SDClient.instance

            async def txt2img(
                prompt: str,
                negative_prompt: str,
                width: int,
                height: int,
                num_inference_steps: int,
                guidance_scale: float,
            ):
                result = sd.txt2img(
                    prompt=prompt,
                    negative_prompt=negative_prompt,
                    num_inference_steps=num_inference_steps,
                    guidance_scale=guidance_scale,
                    width=width,
                    height=height,
                )

                torch.cuda.empty_cache()

                yield result.images[0]

            with gr.Tab("Image"):
                with gr.Row():
                    with gr.Column():
                        prompt = gr.TextArea("", lines=4, label="Prompt")
                        negative_prompt = gr.TextArea(
                            "", lines=4, label="Negative Prompt"
                        )
                        with gr.Row():
                            width = gr.Slider(
                                minimum=256,
                                maximum=2048,
                                value=512,
                                step=8,
                                interactive=True,
                                label="Width",
                            )
                            height = gr.Slider(
                                minimum=256,
                                maximum=2048,
                                value=512,
                                step=8,
                                interactive=True,
                                label="Height",
                            )
                        steps = gr.Slider(
                            minimum=1,
                            maximum=100,
                            value=20,
                            step=1,
                            interactive=True,
                            label="Steps",
                        )
                        guidance_scale = gr.Slider(
                            minimum=0,
                            maximum=50,
                            value=3,
                            step=1,
                            interactive=True,
                            label="Guidance Scale",
                        )
                        btn = gr.Button("Generate")
                    with gr.Column():
                        img_output = gr.Image(
                            None,
                            width=512,
                            height=512,
                            interactive=False,
                            label="Output",
                        )
                    btn.click(
                        fn=txt2img,
                        inputs=[
                            prompt,
                            negative_prompt,
                            width,
                            height,
                            steps,
                            guidance_scale,
                        ],
                        outputs=[img_output],
                    )

            with gr.Tab("Video"):
                with gr.Row():
                    with gr.Column():
                        gr.Image(None, width=512, height=512, label="Input Image")
                    with gr.Column():
                        gr.PlayableVideo(
                            None,
                            width=320,
                            height=320,
                            interactive=False,
                            label="Output",
                        )

        web_ui.launch(prevent_thread_lock=prevent_thread_lock)


if __name__ == "__main__":
    launch_webui(True)
