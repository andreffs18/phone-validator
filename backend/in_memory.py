from logging import Logger
from typing import Union

from starlette.applications import Starlette

from services import read_prefix_file


async def get_prefix(request, phone_number: str) -> Union[str, bool]:
    for prefix in request.app.state.PREFIXES:
        if phone_number.startswith(prefix):
            return prefix
    return False


async def startup_backend(app: Starlette, logger: Logger) -> None:
    app.state.PREFIXES = read_prefix_file()
    logger.info(f"Ready to go with {len(app.state.PREFIXES)} lines")


async def shutdown_backend(app: Starlette, logger: Logger) -> None:
    app.state.PREFIXES = []
    logger.info("Cleaned list of prefixes")
