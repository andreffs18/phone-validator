import importlib
import logging
import os
import time

import uvicorn
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.routing import Route
from starlette_prometheus import PrometheusMiddleware, metrics

from routes import aggregate, health

logger = logging.getLogger("uvicorn")
logger.setLevel(logging.DEBUG)

# You can override with a .env for any one of them under the "backends/" folder
BACKEND = importlib.import_module(os.environ.get("BACKEND", "backend.trie"))


async def startup():
    start_time = time.time()
    logger.info(f'Starting up with "{BACKEND.__name__}"...')
    await BACKEND.startup_backend(app, logger)
    app.state.get_prefix = BACKEND.get_prefix
    logger.info(f"Ready to receive traffic [TTS: {round(time.time() - start_time, 2)} secs]")


async def shutdown():
    logger.info("Shutting down...")
    await BACKEND.shutdown_backend(app, logger)


def init_server():
    logger.info("🌀 Starting app...")
    return Starlette(
        debug=os.environ.get("DEBUG", True),
        routes=[
            Route("/", health),
            Route("/aggregate", aggregate, methods=["POST"]),
            Route("/metrics", metrics),
        ],
        middleware=[Middleware(PrometheusMiddleware)],
        on_startup=[startup],
        on_shutdown=[shutdown],
    )


app = init_server()

if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8080, reload=True)
