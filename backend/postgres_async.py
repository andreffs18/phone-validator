from logging import Logger
from typing import Union

import psycopg
from starlette.applications import Starlette

from services import read_prefix_file


async def get_prefix(request, phone_number: str) -> Union[str, bool]:
    async with await psycopg.AsyncConnection.connect(
        "postgresql://postgres:postgres@postgres:5432/postgres"
    ) as postgres_client:
        async with postgres_client.cursor() as cur:
            await cur.execute(
                f"SELECT * FROM prefix WHERE '{phone_number}' LIKE '%' || prefix || '%' ORDER BY prefix DESC LIMIT 1"
            )
            result = await cur.fetchone()

    if not result:
        return False
    return result[0]


async def startup_backend(app: Starlette, logger: Logger) -> None:
    prefixes = read_prefix_file()

    async with await psycopg.AsyncConnection.connect(
        "postgresql://postgres:postgres@postgres:5432/postgres"
    ) as postgres_client:
        async with postgres_client.cursor() as cur:
            await cur.execute("CREATE TABLE IF NOT EXISTS prefix (prefix INT PRIMARY KEY NOT NULL);")

            amount = 5000
            chunks = [prefixes[i : i + amount] for i in range(0, len(prefixes), amount)]
            for prefixes in chunks:
                prefixes = ",".join([f"({prefix})" for prefix in prefixes])
                # setup column "prefix" with all lines as rows
                await cur.execute(f"INSERT INTO prefix (prefix) VALUES {prefixes} ON CONFLICT (prefix) DO NOTHING;")

    logger.info('Ready to go with postgres database "postgres"')


async def shutdown_backend(app: Starlette, logger: Logger) -> None:
    async with await psycopg.AsyncConnection.connect(
        "postgresql://postgres:postgres@postgres:5432/postgres"
    ) as postgres_client:
        async with postgres_client.cursor() as cur:
            await cur.execute("DROP TABLE prefix;")

    logger.info('Dropped "postgres" postgres database')
