from settings import TTS_VOICES_PATH
from utils.startup_args import startup_args
import gradio as gr
import os
from utils.webui_functions import (
    set_language,
    set_speed,
    set_temperature,
    set_voice,
    preview_speech,
    chat,
    generate_video,
    txt2img,
    audiogen,
    musicgen,
    disable_send_button,
    shape_generate,
    settings,
)


def launch_webui(args, prevent_thread_lock=False):

    use_tts = args is None or args.all or args.tts
    use_llm = args is None or args.all or args.llm
    use_sd = args is None or args.all or args.llm

    with gr.Blocks(title="monofy-ai", analytics_enabled=False).queue() as web_ui:
        if use_llm:
            with gr.Tab("Chat"):
                speech_checkbox = None

                with gr.Row():
                    with gr.Column():
                        with gr.Row():
                            speech_checkbox = gr.Checkbox(
                                value=use_tts,
                                interactive=use_tts,
                                visible=use_tts,
                                label="Speak results",
                            )
                            check_sentences_checkbox = gr.Checkbox(
                                value=True,
                                label="Chunk sentences",
                                visible=False,  # TODO
                            )
                        gr.ChatInterface(
                            fn=chat,
                            additional_inputs=[
                                speech_checkbox,
                                check_sentences_checkbox,
                            ],
                        ).queue()

        if use_tts:
            with gr.Tab("TTS"):

                with gr.Column():
                    grText = gr.Textbox(
                        "This is a test of natural speech.", label="Text"
                    )
                    tts_voice = gr.Textbox(
                        os.path.join(TTS_VOICES_PATH, "female1.wav"),
                        label="Voice",
                    )
                    with gr.Row():
                        tts_speed = gr.Number("1", label="Speed")
                        tts_temperature = gr.Number("0.75", label="Temperature")
                        tts_top_p = gr.Number("0.85", label="Top Percentile")
                        tts_language = gr.Dropdown(
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
                        tts_language.change(set_language, inputs=[tts_language])
                        tts_speed.change(set_speed, inputs=[tts_speed])
                        tts_temperature.change(
                            set_temperature, inputs=[tts_temperature]
                        )
                    tts_voice.change(set_voice, inputs=[tts_voice])
                    tts_button = gr.Button("Generate")
                    tts_output = gr.Audio(
                        label="Audio Output",                        
                        autoplay=True,
                        format="wav",
                        interactive=False,
                        streaming=True,
                    )
                    tts_button.click(
                        preview_speech,
                        inputs=[
                            grText,
                            tts_speed,
                            tts_temperature,
                            tts_top_p,
                            tts_voice,
                            tts_language,
                        ],
                        outputs=[tts_output],
                    )

        if use_sd:

            t2i_vid_button: gr.Button = None

            with gr.Tab("Image/Video"):
                with gr.Row():
                    with gr.Column():
                        t2i_prompt = gr.TextArea(
                            "an advanced humanoid robot with human expression in a futuristic laboratory",
                            lines=4,
                            label="Prompt",
                        )
                        t2i_negative_prompt = gr.TextArea(
                            "", lines=4, label="Negative Prompt"
                        )
                        with gr.Row():
                            t2i_width = gr.Slider(
                                minimum=256,
                                maximum=2048,
                                value=512,
                                step=32,
                                interactive=True,
                                label="Width",
                            )
                            t2i_height = gr.Slider(
                                minimum=256,
                                maximum=2048,
                                value=512,
                                step=32,
                                interactive=True,
                                label="Height",
                            )
                        t2i_steps = gr.Slider(
                            minimum=1,
                            maximum=100,
                            value=20,
                            step=1,
                            interactive=True,
                            label="Steps",
                        )
                        t2i_guidance_scale = gr.Slider(
                            minimum=0,
                            maximum=50,
                            value=3,
                            step=0.1,
                            interactive=True,
                            label="Guidance",
                        )
                        t2i_button = gr.Button("Generate")
                    with gr.Column():
                        t2i_output = gr.Image(
                            None,
                            width=512,
                            height=512,
                            interactive=False,
                            label="Output",
                        )
                        with gr.Row():
                            i2v_width = gr.Number(
                                512, label="Width", precision=0, step=32
                            )
                            i2v_height = gr.Number(
                                512, label="Height", precision=0, step=32
                            )
                            i2v_fps = gr.Number(6, label="FPS", precision=0, minimum=1)
                            i2v_steps = gr.Number(10, label="Steps", precision=0)
                            i2v_motion = gr.Number(
                                15, label="Motion Bucket ID", precision=0
                            )
                            i2v_noise = gr.Number(
                                0.0,
                                label="Noise (also increases motion)",
                                precision=0,
                                step=0.01,
                            )
                            i2v_interpolation = gr.Number(
                                3, label="Frame Interpolation", precision=0, minimum=1
                            )

                        t2i_vid_button = gr.Button("Generate Video", interactive=False)

                        i2v_output = gr.Video(
                            None,
                            width=320,
                            height=320,
                            interactive=False,
                            label="Video",
                            format="mp4",
                            autoplay=True,
                        )

                        t2i_vid_button.click(
                            generate_video,
                            inputs=[
                                t2i_output,
                                i2v_width,
                                i2v_height,
                                i2v_steps,
                                i2v_fps,
                                i2v_motion,
                                i2v_noise,
                                i2v_interpolation,
                            ],
                            outputs=[i2v_output],
                        )

                    t2i_button.click(disable_send_button, outputs=[t2i_vid_button])
                    t2i_button.click(
                        txt2img,
                        inputs=[
                            t2i_prompt,
                            t2i_negative_prompt,
                            t2i_width,
                            t2i_height,
                            t2i_steps,
                            t2i_guidance_scale,
                        ],
                        outputs=[t2i_output, t2i_vid_button],
                    )

            with gr.Tab("Audio/Music"):
                with gr.Row():
                    with gr.Column():
                        audiogen_prompt = gr.TextArea(
                            "peaceful forest sounds",
                            label="Audio description",
                            lines=3,
                        )
                        with gr.Row():
                            audiogen_duration = gr.Slider(
                                minimum=1,
                                maximum=30,
                                value=3,
                                step=1,
                                interactive=True,
                                label="Duration (seconds)",
                            )
                            audiogen_temperature = gr.Slider(
                                minimum=0.1,
                                maximum=1.9,
                                value=1,
                                step=0.05,
                                interactive=True,
                                label="Temperature",
                            )
                        audiogen_button = gr.Button("Generate Audio")
                        audiogen_output = gr.Audio(interactive=False)
                        audiogen_button.click(
                            audiogen,
                            inputs=[
                                audiogen_prompt,
                                audiogen_duration,
                                audiogen_temperature,
                            ],
                            outputs=[audiogen_output],
                        )
                    with gr.Column():
                        musicgen_prompt = gr.TextArea(
                            "lofi hip-hop, smooth bassline, old piano, boom bap",
                            label="Music description",
                            lines=3,
                        )
                        with gr.Accordion("Settings"):
                            musicgen_duration = gr.Slider(
                                minimum=1,
                                maximum=30,
                                value=15,
                                step=1,
                                interactive=True,
                                label="Duration (seconds)",
                            )
                            musicgen_temperature = gr.Slider(
                                minimum=0.1,
                                maximum=1.9,
                                value=0.75,
                                step=0.05,
                                interactive=True,
                                label="Temperature",
                            )
                            musicgen_guidance = gr.Slider(
                                minimum=0.1,
                                maximum=10,
                                value=6.5,
                                step=0.25,
                                interactive=True,
                                label="Guidance Scale",
                            )
                            musicgen_top_p = gr.Slider(
                                minimum=0.1,
                                maximum=1,
                                value=0.97,
                                step=0.25,
                                interactive=True,
                                label="Top Percentile",
                            )
                        musicgen_button = gr.Button("Generate Music")
                        musicgen_output = gr.Audio(interactive=False)
                        musicgen_video = gr.Video(interactive=False)
                        musicgen_button.click(
                            musicgen,
                            inputs=[
                                musicgen_prompt,
                                musicgen_duration,
                                musicgen_temperature,
                                musicgen_guidance,
                                musicgen_top_p,
                            ],
                            outputs=[musicgen_output, musicgen_video],
                        )
            with gr.Tab("Shap-e"):
                with gr.Row():
                    with gr.Column():
                        shap_e_prompt = gr.TextArea(
                            "a humanoid robot", label="Prompt"
                        )
                        shap_e_guidance = gr.Slider(
                            minimum=0,
                            maximum=50,
                            value=15,
                            step=0.1,
                            interactive=True,
                            label="Guidance",
                        )
                        shap_e_steps = gr.Slider(
                            minimum=1,
                            maximum=100,
                            value=20,
                            step=1,
                            interactive=True,
                            label="Steps",
                        )
                        shap_e_button = gr.Button("Generate")
                    with gr.Column():
                        shap_e_output = gr.Model3D(
                            None,
                            interactive=False,
                            label="Output",
                        )
                        shap_e_button.click(
                            shape_generate,
                            inputs=[
                                shap_e_prompt,
                                shap_e_steps,
                                shap_e_guidance,
                            ],
                            outputs=[shap_e_output],
                        )

        web_ui.launch(
            prevent_thread_lock=prevent_thread_lock, inbrowser=args and not args.all
        )

        return web_ui


if __name__ == "__main__":
    print("Loading webui in main thread.")
    launch_webui(startup_args)
