import logging
from fastapi import Depends, HTTPException
from classes.requests import Txt2ImgRequest
from modules.plugins import PluginBase, release_plugin, use_plugin
from modules.filter import filter_request
from plugins.stable_diffusion import format_response
from plugins.txt2img_canny import Txt2ImgCannyPlugin
from settings import SD_USE_SDXL
from utils.stable_diffusion_utils import postprocess


class Txt2ImgDepthMidasPlugin(Txt2ImgCannyPlugin):

    name = "Stable Diffusion (Depth IP Adapter)"
    description = "Stable Diffusion text-to-image using provided depth map as guidance."
    instance = None

    def __init__(self):
        super().__init__(
            "TencentARC/t2i-adapter-depth-midas-sdxl-1.0"
            if SD_USE_SDXL
            else "TencentARC/t2i-adapter-depth-midas-1.0"
        )


@PluginBase.router.post("/txt2img/depth", tags=["Image Generation"])
async def txt2img(
    req: Txt2ImgRequest,
):
    plugin = None
    try:
        req = filter_request(req)
        plugin: Txt2ImgDepthMidasPlugin = await use_plugin(Txt2ImgDepthMidasPlugin)
        # input_image = get_image_from_request(req.image, (req.width, req.height))
        image = await plugin.generate(req)
        image, json_response = await postprocess(image, req)
        return format_response(req, json_response, image)
    except Exception as e:
        logging.error(e, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if plugin is not None:
            release_plugin(Txt2ImgDepthMidasPlugin)


@PluginBase.router.get("/txt2img/depth", tags=["Image Generation"])
async def txt2img_from_url(
    req: Txt2ImgRequest = Depends(),
):
    return await txt2img(req)
