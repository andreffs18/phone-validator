from logging import Logger
from typing import Union

from pytrie import StringTrie
from starlette.applications import Starlette

from services import read_prefix_file


async def get_prefix(request, phone_number: str) -> Union[str, bool]:
    return request.app.state.trie.longest_prefix(phone_number, default=None)


async def startup_backend(app: Starlette, logger: Logger) -> None:
    trie = StringTrie()
    for p in read_prefix_file():
        trie[p] = True

    app.state.trie = trie
    logger.info(f"Ready to go with {len(app.state.trie)} lines")


async def shutdown_backend(app: Starlette, logger: Logger) -> None:
    app.state.trie = None
    logger.info("Cleaned list of prefixes")
