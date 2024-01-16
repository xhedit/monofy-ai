import logging
import os
from fastapi import BackgroundTasks, HTTPException
from fastapi.responses import FileResponse
from fastapi.routing import APIRouter
from utils.gpu_utils import gpu_thread_lock
from utils.file_utils import delete_file, random_filename

router = APIRouter()


@router.get("/audiogen")
async def audiogen(
    background_tasks: BackgroundTasks,
    prompt: str,
    duration: int = 3,
    temperature: float = 1.0,
    cfg_coef: float = 3.0,
):
    try:
        from clients import AudioGenClient

        async with gpu_thread_lock:
            file_path_noext = random_filename(None, True)
            file_path = AudioGenClient.generate(
                prompt,
                file_path_noext,
                duration=duration,
                temperature=temperature,
                cfg_coef=cfg_coef,
            )
            background_tasks.add_task(delete_file, file_path)
            return FileResponse(os.path.abspath(file_path), media_type="audio/wav")
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail=str(e))