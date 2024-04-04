import logging
import huggingface_hub
import imageio
import numpy as np
from safetensors import safe_open
from typing import Optional
from PIL import Image
from fastapi import Depends
from fastapi.responses import FileResponse
from pydantic import BaseModel
import torch
from classes.animatelcm_scheduler import AnimateLCMSVDStochasticIterativeScheduler
from classes.animatelcm_pipeline import StableVideoDiffusionPipeline
from modules.plugins import PluginBase, use_plugin, release_plugin
from utils.file_utils import random_filename
from utils.gpu_utils import set_seed
from utils.image_utils import get_image_from_request
from utils.video_utils import frames_to_video, interpolate_frames
from settings import (
    IMG2VID_DECODE_CHUNK_SIZE,
    IMG2VID_DEFAULT_FRAMES,
    IMG2VID_DEFAULT_MOTION_BUCKET,
    HYPERTILE_VIDEO,
)


class Img2VidXTRequest(BaseModel):
    image: str = None
    motion_bucket: Optional[int] = IMG2VID_DEFAULT_MOTION_BUCKET
    num_inference_steps: Optional[int] = 6
    width: Optional[int] = 512
    height: Optional[int] = 512
    fps: Optional[int] = 12
    num_frames: Optional[int] = IMG2VID_DEFAULT_FRAMES
    noise: Optional[float] = 0
    interpolate: Optional[int] = 1
    seed: Optional[int] = -1
    audio_url: Optional[str] = None


class Img2VidXTPlugin(PluginBase):

    name = "img2vid"
    description = "Image-to-video generation"
    instance = None

    def __init__(self):
        import logging
        from settings import SVD_MODEL
        from utils.gpu_utils import autodetect_dtype

        super().__init__()

        self.dtype = autodetect_dtype(bf16_allowed=False)

        try:

            noise_scheduler = AnimateLCMSVDStochasticIterativeScheduler(
                num_train_timesteps=40,
                sigma_min=0.002,
                sigma_max=700.0,
                sigma_data=1.0,
                s_noise=1.0,
                rho=7,
                clip_denoised=False,
            )

            pipe = StableVideoDiffusionPipeline.from_pretrained(
                SVD_MODEL,
                scheduler=noise_scheduler,
                use_safetensors=True,
                torch_dtype=self.dtype,
                variant="fp16",
            )

            pipe.to(self.device)

            self.resources["pipeline"] = pipe

            path = huggingface_hub.hf_hub_download(
                "wangfuyun/AnimateLCM-SVD-xt", "AnimateLCM-SVD-xt-1.1.safetensors"
            )

            self.model_select(path)

            # pipe.enable_sequential_cpu_offload()
            pipe.enable_model_cpu_offload()

        except Exception as e:
            logging.error(
                "You may need to launch with --login and supply a huggingface token to download this model."
            )
            raise e

    def model_select(self, file_path):
        pipe = self.resources["pipeline"]
        print("load model weights", file_path)
        pipe.unet.cpu()
        state_dict = {}
        with safe_open(file_path, framework="pt", device="cpu") as f:
            for key in f.keys():
                state_dict[key] = f.get_tensor(key)
        missing, unexpected = pipe.unet.load_state_dict(state_dict, strict=True)
        pipe.unet.cuda()
        del state_dict
        return


@PluginBase.router.post("/img2vid/xt", response_class=FileResponse)
async def img2vid(req: Img2VidXTRequest):

    plugin = None

    try:
        plugin = await use_plugin(Img2VidXTPlugin)

        pipe = plugin.resources["pipeline"]

        from hyper_tile.hyper_tile import split_attention

        # if image is not None:
        #    image: Image.Image = Image.open(image.file).convert("RGB")

        width = req.width
        height = req.height
        image: Image.Image = get_image_from_request(req.image, (width * 2, height * 2))

        aspect_ratio = width / height
        if aspect_ratio < 1:  # portrait
            image = image.crop((0, 0, image.height * aspect_ratio, image.height))
        elif aspect_ratio > 1:  # landscape
            image = image.crop((0, 0, image.width, image.width / aspect_ratio))
        else:  # square
            dim = min(image.width, image.height)
            image = image.crop((0, 0, dim, dim))

        image = image.resize((width, height), Image.Resampling.BICUBIC)

        def gen():

            # clear vram if we are using any shared memory
            if torch.cuda.is_available():
                shared_used = torch.cuda.memory_reserved()
                if shared_used > 0:
                    torch.cuda.empty_cache()

            set_seed(req.seed)
            with torch.autocast("cuda"):
                frames = pipe(
                    image,
                    decode_chunk_size=IMG2VID_DECODE_CHUNK_SIZE,
                    num_inference_steps=req.num_inference_steps,
                    num_frames=req.num_frames,
                    width=width,
                    height=height,
                    motion_bucket_id=req.motion_bucket,
                    noise_aug_strength=req.noise,
                    min_guidance_scale=1,
                    max_guidance_scale=1.2,
                ).frames[0]

            if req.interpolate > 0:
                frames = interpolate_frames(frames, req.interpolate)

            filename_noext = random_filename()
            filename = f"{filename_noext}-0.mp4"

            logging.info(
                "Output FPS = "
                + str(req.fps)
                + " with interpolate = "
                + str(req.interpolate)
            )

            with imageio.get_writer(
                filename, format="mp4", fps=req.fps
            ) as video_writer:
                for frame in frames:
                    try:
                        video_writer.append_data(np.array(frame))
                    except Exception as e:
                        logging.error(e)

                video_writer.close()

            if req.audio_url:
                frames_to_video(
                    filename, filename, fps=req.fps, audio_url=req.audio_url
                )

            print(f"Returning {filename}...")

            return FileResponse(filename, media_type="video/mp4", filename="video.mp4")

        if HYPERTILE_VIDEO:
            aspect_ratio = 1 if width == height else width / height
            with split_attention(
                plugin.pipeline.vae,
                tile_size=256,
                aspect_ratio=aspect_ratio,
            ):
                with split_attention(
                    plugin.pipeline.unet,
                    tile_size=256,
                    aspect_ratio=aspect_ratio,
                ):
                    return gen()
        else:
            return gen()
    except Exception as e:
        logging.error(e, exc_info=True)
        raise e

    finally:
        if plugin is not None:
            release_plugin(Img2VidXTPlugin)


@PluginBase.router.get("/img2vid/xt", response_class=FileResponse)
async def img2vid_from_url(req: Img2VidXTRequest = Depends()):
    return await img2vid(req)
