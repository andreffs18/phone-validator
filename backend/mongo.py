from logging import Logger
from typing import Union

import motor.motor_asyncio
from starlette.applications import Starlette

from services import read_prefix_file


async def get_prefix(request, phone_number: str) -> Union[str, bool]:
    mongo_client = motor.motor_asyncio.AsyncIOMotorClient("mongo", 27017)
    # explode phone number in a list of sub-numbers
    # eg: phone_number = "1234" -> ["1234", "123", "12", "1"]
    prefixes = [phone_number[:index] for index in range(len(phone_number), 0, -1)]
    result = await mongo_client.test.test_value.find_one({"prefix": {"$in": prefixes}})
    if not result:
        return False

    return result["prefix"]


async def startup_backend(app: Starlette, logger: Logger) -> None:
    mongo_client = motor.motor_asyncio.AsyncIOMotorClient("mongo", 27017)
    # create index on prefix column with ascending sort order
    await mongo_client.test.test_value.create_index([("prefix", "1")], background=True)

    prefixes = read_prefix_file()
    # one object per key, with the actual line being the value of the "key" field
    await mongo_client.test.test_value.insert_many(map(lambda prefix: {"prefix": prefix}, prefixes))
    # deallocate memory from list of 900k prefixes
    del prefixes
    logger.info('Ready to go with mongo database "test"')


async def shutdown_backend(app: Starlette, logger: Logger) -> None:
    mongo_client = motor.motor_asyncio.AsyncIOMotorClient("mongo", 27017)
    await mongo_client.drop_database("test")
    logger.info('Dropped "test" mongo database')
