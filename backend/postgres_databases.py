import asyncio
from datetime import datetime
from logging import Logger
from typing import Any, List, Union

from databases import Database
from starlette.applications import Starlette

from services import read_prefix_file


database = Database("postgresql://postgres:postgres@postgres:5432/postgres", min_size=10, max_size=20)


async def get_prefix(request, phone_number: str) -> Union[str, bool]:
    async with database as conn:
        result = await conn.execute(
            f"SELECT * FROM prefix WHERE '{phone_number}' LIKE '%' || prefix || '%' ORDER BY prefix DESC LIMIT 1"
        )

    if not result:
        return False
    return result


async def startup_backend(app: Starlette, logger: Logger) -> None:
    prefixes = read_prefix_file()

    async with database as conn:
        await conn.execute("CREATE TABLE IF NOT EXISTS prefix (prefix INT PRIMARY KEY NOT NULL);")

        coroutines = []
        for prefixes in _chunkit(prefixes, 10000):
            prefixes = ",".join([f"({prefix})" for prefix in prefixes])
            # setup column "prefix" with all lines as rows
            coroutines.append(
                conn.execute(f"INSERT INTO prefix (prefix) VALUES {prefixes} ON CONFLICT (prefix) DO NOTHING;")
            )

        for group in _chunkit(coroutines, 4):
            logger.debug(f"{datetime.utcnow()} Inserting 4 groups of 10000 prefixes...")
            await asyncio.gather(*group)

    logger.info('Ready to go with postgres database "postgres"')


def _chunkit(elements: List, size: int) -> List[List[Any]]:
    return [elements[i : i + size] for i in range(0, len(elements), size)]


async def shutdown_backend(app: Starlette, logger: Logger) -> None:
    # async with database as conn:
        # await conn.execute("DROP TABLE prefix;")

    await database.disconnect()
    logger.info('Dropped "postgres" postgres database')
