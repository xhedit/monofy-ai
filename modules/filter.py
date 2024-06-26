import logging
from fastapi import HTTPException

from classes.requests import Txt2ImgRequest
from settings import SD_DEFAULT_MODEL_INDEX, SD_MODELS
from utils.text_utils import translate_emojis


def filter_request(req: Txt2ImgRequest):

    req.model_index = req.model_index or SD_DEFAULT_MODEL_INDEX
    model_name = SD_MODELS[req.model_index]
    is_xl = "xl" in model_name.lower()
    is_turbo = "turbo" in model_name.lower()
    is_lightning = "lightning" in model_name.lower()

    if not req.num_inference_steps:
        req.num_inference_steps = 10 if is_lightning else 14 if is_turbo else 25

    if not req.width:
        req.width = 768 if is_xl else 512
    if not req.height:
        req.height = 768 if is_xl else 512

    aspect_ratio = req.width / req.height

    if req.image and (
        req.width > 1920 or req.height > 1920 or req.width * req.height > 1920 * 1920
    ):
        if req.width > req.height:
            req.width = 1920
            req.height = int(1920 / aspect_ratio)
        else:
            req.height = 1920
            req.width = int(1920 * aspect_ratio)

    if req.width < 64 or req.height < 64:
        raise HTTPException(400, "Image dimensions should be at least 64x64")

    if req.width % 64 != 0 or req.height % 64 != 0:
        req.width = req.width - (req.width % 64)
        req.height = req.height - (req.height % 64)
        logging.warning(
            f"Image dimensions should be multiples of 64. Cropping to {req.width}x{req.height}"
        )
    if not req.num_inference_steps:
        model_path: str = SD_MODELS[req.model_index]
        req.num_inference_steps = 12 if "xl" in model_path.lower() else 24

    prompt = translate_emojis(req.prompt)
    words = prompt.lower().replace(",", " ").split(" ")

    if req.negative_prompt is None:
        req.negative_prompt = ""

    # Prompts will be rejected if they contain any of these (including partial words).
    # There is honestly no way to block every word, but this should send a clear message to the offending user.
    banned_partials = [
        "infant",
        "baby",
        "babby", # how is it formed?
        "child",
        "toddler",
        "boys",
        "girls",
        "teen",  # Sorry Bruce Springsteen, I'm the boss here.
        "underage",
        "pubesc",
        "minor",
        "school",
        "student",
    ]

    banned_words = [
        "boy",  # "Playboy" allowed, "boy" not allowed. Sorry Boy George.
        "girl",  # "Batgirl" allowed, "girl" not allowed.
    ]

    # These words are banned only if they are complete words to prevent false positives.
    # For example, "kid" is banned, but "kidney" is not when performing a request that could be nsfw.
    banned_nsfw_words = [
        "kid",  # Sorry Kid Rock and Billy the Kid, you are in sfw prompts only.
    ]

    # (partials) These automatically trigger nsfw. I am not going to include a comprehensive list of
    # filthy words because it's impossible and exhausting. This is just to prevent accidental nsfw prompts.
    nsfw_partials = [
        "nud",
        "naked",
        "porn",
        "nsfw",
        "sex",
        "boob",
        "breast",
        "penis",
        "vagin",
        "dick",
        "cock",
        "puss",
        "lick",
        "suck",
        "blow",
        "genital",
        "titt",
    ]

    # If NSFW, ban these additional words that are not explicitly banned
    # because they are too restrictive for sfw, too vague, or parts of other words
    banned_nsfw_partials = ["baby", "kid", "teen", "boy", "girl"]

    # force these negative prompts to prevent further "accidents"
    negative_prompt = "child, teenager"
    if not req.nsfw:
        negative_prompt += ", nudity, nsfw"

    for word in words:

        word = word.lower()

        if word in banned_words:
            raise HTTPException(406, "Prohibited prompt")

        for banned in banned_partials:
            if banned in word:
                raise HTTPException(406, "Prohibited prompt")

        if req.nsfw:
            if word in banned_nsfw_words:
                raise HTTPException(406, "Prohibited prompt")
            for banned in banned_nsfw_partials:
                if banned in word:
                    raise HTTPException(406, "Prohibited prompt")

        else:
            for banned in nsfw_partials:
                if banned in word:
                    raise HTTPException(406, "Prohibited prompt")

    return req
