import logging
import os
import random
import string
import requests
from huggingface_hub import snapshot_download
from settings import MEDIA_CACHE_DIR


def ensure_folder_exists(path: str):
    if not os.path.exists(path):
        os.makedirs(path)
        logging.info(f"Created folder {path}")


def cached_snapshot(model_name: str):

    user_path = os.path.join(os.path.expanduser("~"), ".cache", "huggingface", "hub")

    local_dir = (
        user_path + "/models--" + model_name.replace("/", "--").replace(":", "--")
    )

    if os.path.isdir(local_dir):
        
        if os.path.isdir(os.path.join(local_dir, "snapshots")):
            snapshots_folder = os.path.join(local_dir, "snapshots")
            first_subfolder = os.listdir(snapshots_folder)[0]
            return os.path.abspath(os.path.join(local_dir, "snapshots", first_subfolder))
        
        return local_dir
    
    logging.info(f"Downloading {model_name} to {local_dir}")

    s = model_name.split(":")
    if len(s) == 2:
        model_name = s[0]
        revision = s[1]
    else:
        revision = "main"

    return snapshot_download(
        repo_id=model_name,
        revision=revision,
        local_dir=local_dir,
    )


def delete_file(file_path: str):
    try:
        os.remove(file_path)
        logging.info(f"Deleted {file_path}")
    except Exception as e:
        logging.error(f"Error deleting {file_path}: {e}")


def random_filename(
    file_extension: str = None, include_cache_path=True, length: int = 10
):
    filename = "".join(random.choice(string.ascii_letters) for _ in range(length))
    if include_cache_path:
        filename = os.path.join(MEDIA_CACHE_DIR, filename)
    if file_extension is not None:
        filename += f".{file_extension}"
    return filename


def download_to_cache(url: str):
    # Extract the extension from the URL
    extension = url.split(".")[-1]

    url_hash = str(abs(hash(url)).to_bytes(8, "big").hex())
    filename = os.path.join(MEDIA_CACHE_DIR, f"{url_hash}.{extension}")

    if os.path.exists(filename):
        logging.info(f"Using cached file: {filename}")
    else:
        logging.info(f"Downloading {url} to {filename}")
        r = requests.get(url, allow_redirects=True)
        with open(filename, "wb") as f:
            f.write(r.content)

    return filename
