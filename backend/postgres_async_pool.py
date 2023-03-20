import asyncio
from datetime import datetime
from logging import Logger
from typing import Any, List, Union

import psycopg
import psycopg_pool
from starlette.applications import Starlette

from services import read_prefix_file

_postgres_client = None


def get_postgres_client() -> psycopg.AsyncConnection:
    global _postgres_client
    if not _postgres_client:
        _postgres_client = psycopg_pool.AsyncConnectionPool(
            "postgresql://postgres:postgres@postgres:5432/postgres", open=True
        )
    return _postgres_client


async def get_prefix(request, phone_number: str) -> Union[str, bool]:
    postgres_client = get_postgres_client()
    async with postgres_client.connection() as connection:
        async with connection.cursor() as cur:
            await cur.execute(
                f"SELECT * FROM prefix WHERE '{phone_number}' LIKE '%' || prefix || '%' ORDER BY prefix DESC LIMIT 1"
            )
            result = await cur.fetchone()

    if not result:
        return False
    return result[0]


async def startup_backend(app: Starlette, logger: Logger) -> None:
    prefixes = read_prefix_file()

    postgres_client = get_postgres_client()
    async with postgres_client.connection() as connection:
        async with connection.cursor() as cur:
            await cur.execute("CREATE TABLE IF NOT EXISTS prefix (prefix INT PRIMARY KEY NOT NULL);")

            coroutines = []
            for prefixes in _chunkit(prefixes, 10000):
                prefixes = ",".join([f"({prefix})" for prefix in prefixes])
                # setup column "prefix" with all lines as rows
                coroutines.append(
                    cur.execute(f"INSERT INTO prefix (prefix) VALUES {prefixes} ON CONFLICT (prefix) DO NOTHING;")
                )

            for group in _chunkit(coroutines, 4):
                logger.debug(f"{datetime.utcnow()} Inserting 4 groups of 10000 prefixes...")
                await asyncio.gather(*group)

    logger.info('Ready to go with postgres database "postgres"')


def _chunkit(elements: List, size: int) -> List[List[Any]]:
    return [elements[i : i + size] for i in range(0, len(elements), size)]


async def shutdown_backend(app: Starlette, logger: Logger) -> None:
    postgres_client = get_postgres_client()
    async with postgres_client.connection() as connection:
        async with connection.cursor() as cur:
            await cur.execute("DROP TABLE prefix;")

    await postgres_client.close()
    logger.info('Dropped "postgres" postgres database')
