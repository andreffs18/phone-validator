import logging
import os
from typing import List, Union

import requests
from pydantic import BaseModel

logger = logging.getLogger("uvicorn")
logger.setLevel(logging.DEBUG)


class Response(BaseModel):
    """
    Example:
        {'number': '+1478192', 'sector': 'Clothing'}
    """

    number: str
    sector: str


async def get_sector(phone_number: str) -> str:
    response = requests.get(f"http://mock:4010/sector/{phone_number}")
    response = Response(**response.json())
    return response.sector


def is_valid_phone_number(phone_number: str) -> Union[str, bool]:
    """
    A phone number is considered valid if:
    * all dashes and parenteses are ignored
    * an optional leading `+` or `00`
    * whitespace anywhere except immediately after the `+`.
    * has exactly 3 digits or more than 6 and less than 13
    * it contains only digits,
    """
    phone_number = phone_number.replace("-", "")
    phone_number = phone_number.replace("(", "")
    phone_number = phone_number.replace(")", "")

    if phone_number.startswith("+") or phone_number.startswith("00"):
        phone_number = phone_number.lstrip("+")
        phone_number = phone_number.lstrip("00")

    if phone_number.startswith(" "):
        logger.debug('number does start with " "')
        return False

    phone_number = phone_number.replace(" ", "")
    if len(phone_number) != 3:
        if not (6 < len(phone_number) < 13):
            return False

    if not phone_number.isdigit():
        logger.debug("number is not a digit")
        return False

    return phone_number


def read_prefix_file(filepath: str = "prefixes.txt") -> List[str]:
    """Auxiliary method to load prefix file and returns a list with all of them"""
    with open(os.path.join(os.getcwd(), filepath)) as tmp:
        prefixes = list(filter(None, map(lambda line: line.strip(), tmp.readlines())))
    return prefixes
