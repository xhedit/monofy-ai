import os
import sys
import time
import logging
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
import uvicorn
import warnings
import modules.plugins as plugins
from starlette.datastructures import URL, Address
from fastapi.staticfiles import StaticFiles
from utils.console_logging import init_logging, show_banner
from utils.file_utils import ensure_folder_exists
from utils.gpu_utils import set_idle_offload_time
from utils.misc_utils import print_completion_time, show_ram_usage, sys_info
from settings import HOST, IDLE_OFFLOAD_TIME, MEDIA_CACHE_DIR, PORT
from modules import webui


warnings.filterwarnings("ignore", category=FutureWarning)
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"  # TensorFlow warnings

API_PREFIX = "/api"

init_logging()

start_time = time.time()
end_time = None
sys_info()
ensure_folder_exists(MEDIA_CACHE_DIR)
set_idle_offload_time(IDLE_OFFLOAD_TIME)

# Add submodule directories to the Python path
submodules_dir = os.path.abspath("submodules")
for submodule in os.listdir(submodules_dir):
    submodule_path = os.path.join(submodules_dir, submodule)
    if os.path.isdir(submodule_path) and submodule_path not in sys.path:
        sys.path.insert(0, submodule_path)

def start_webui():
    from webui import txt2img_webui, txt2vid_webui
    pass

class RealIPMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        x_real_ip = request.headers.get("X-Real-IP")
        if x_real_ip:
            # Create a new request with the client's IP replaced with the value from the X-Real-IP header
            url = URL(scope=request.scope)
            client = Address(x_real_ip, request.client.port)
            headers = request.headers
            request = Request(
                {
                    "type": "http",
                    "http_version": "1.1",
                    "method": request.method,
                    "url": url,
                    "headers": headers,
                    "client": client,
                },
                receive=request._receive,
            )
        response = await call_next(request)
        return response


def start_fastapi():
    global app
    global start_time

    show_ram_usage("Memory used before plugins")
    plugins.load_plugins()
    start_webui()
    show_ram_usage("Memory used after plugins")

    app.include_router(plugins.router, prefix=API_PREFIX)
    app.mount(
        "/public_html", StaticFiles(directory="public_html", html=True), name="static"
    )

    show_ram_usage()
    print_completion_time(start_time, "Server started")

    return app


def print_urls():
    print()
    show_banner()
    print()
    logging.info(f"Assistant: http://{HOST}:{PORT}/public_html")
    logging.info(f"Phone: http://{HOST}:{PORT}/public_html/phone")
    logging.info(f"Sketch Assistant: http://{HOST}:{PORT}/public_html/sketch")
    logging.info(f"Docs URL: http://{HOST}:{PORT}/api/docs")
    logging.info(f"Swagger URL: http://{HOST}:{PORT}/api/docs/swagger")
    print()


app = FastAPI(
    title="monofy-ai",
    description="Simple and multifaceted API for AI",
    version="0.0.2",
    redoc_url="/api/docs",
    docs_url="/api/docs/swagger",
    on_startup=[start_fastapi, print_urls, webui.launch],
)
app.add_middleware(RealIPMiddleware)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # Log the details of the validation error to the console
    print("Validation error occurred:")
    for error in exc.errors():
        logging.error(error)

    # Return a custom JSON response with detailed error information
    return JSONResponse(
        status_code=422, content={"detail": "Validation error", "errors": exc.errors()}
    )


if __name__ == "__main__":
    uvicorn.run(
        app,
        host=HOST,
        port=PORT,
    )
