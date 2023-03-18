from logging import Logger
from typing import Union

import psycopg2
from starlette.applications import Starlette

from services import read_prefix_file


async def get_prefix(request, phone_number: str) -> Union[str, bool]:
    postgres_client = psycopg2.connect(
        database="postgres", user="postgres", password="postgres", host="postgres", port="5432"
    )
    cur = postgres_client.cursor()
    cur.execute(f"SELECT * FROM prefix WHERE '{phone_number}' LIKE '%' || prefix || '%' ORDER BY prefix DESC LIMIT 1")
    result = cur.fetchone()

    if not result:
        return False
    return result[0]


async def startup_backend(app: Starlette, logger: Logger) -> None:
    postgres_client = psycopg2.connect(
        database="postgres", user="postgres", password="postgres", host="postgres", port="5432"
    )
    cur = postgres_client.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS prefix (prefix INT PRIMARY KEY NOT NULL);")
    cur.execute(
        "CREATE INDEX IF NOT EXISTS idx_prefix ON public.prefix USING btree "
        "(prefix ASC NULLS LAST) INCLUDE(prefix) TABLESPACE pg_default;"
    )
    prefixes = read_prefix_file()

    # setup column "key" with all lines as rows
    amount = 5000
    chunks = [prefixes[i : i + amount] for i in range(0, len(prefixes), amount)]
    for prefixes in chunks:
        prefixes = ",".join([f"({prefix})" for prefix in prefixes])
        cur.execute(f"INSERT INTO prefix (prefix) VALUES {prefixes} ON CONFLICT (prefix) DO NOTHING;")

    postgres_client.commit()
    logger.info('Ready to go with postgres database "postgres"')


async def shutdown_backend(app: Starlette, logger: Logger) -> None:
    postgres_client = psycopg2.connect(
        database="postgres", user="postgres", password="postgres", host="postgres", port="5432"
    )
    cur = postgres_client.cursor()
    cur.execute("DROP TABLE prefix;")
    postgres_client.commit()
    postgres_client.close()
    logger.info('Dropped "postgres" postgres database')
