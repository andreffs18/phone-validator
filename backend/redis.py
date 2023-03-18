from logging import Logger
from typing import Union

import redis
from starlette.applications import Starlette

from services import read_prefix_file


async def get_prefix(request, phone_number: str) -> Union[str, bool]:
    r = redis.Redis(host="redis", port=6379, db=0)
    # explode phone number in a list of sub-numbers
    # eg: phone_number = "1234" -> ["1234", "123", "12", "1"]
    prefixes = [phone_number[:index] for index in range(len(phone_number), 0, -1)]
    result = r.smismember("prefix", prefixes)
    # parse zipped list of prefixes with an array of returned booleans
    # eg: zip(["1234", "123", "12", "1"], [0, 0, 0, 1]) => ["1"]
    result = list([p for p, r in zip(prefixes, result) if r])
    if not result:
        return False
    return result[0]


async def startup_backend(app: Starlette, logger: Logger) -> None:
    r = redis.Redis(host="redis", port=6379, db=0)

    prefixes = read_prefix_file()
    # create set "prefix" and add all lines as members.
    r.sadd("prefix", *prefixes)
    logger.info('Ready to go with redis database "0"')


async def shutdown_backend(app: Starlette, logger: Logger) -> None:
    r = redis.Redis(host="redis", port=6379, db=0)
    r.flushdb()
    logger.info('Dropped "0" redis database')
