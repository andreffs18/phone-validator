import logging
import time

from starlette.responses import JSONResponse

from services import get_sector, is_valid_phone_number

logger = logging.getLogger("uvicorn")
logger.setLevel(logging.DEBUG)


async def health(request):
    time.sleep(1)
    return JSONResponse({"ok": "ok"}, 200)


async def aggregate(request):
    phone_numbers = await request.json()
    output = {}
    for input_phone_number in phone_numbers:
        phone_number = is_valid_phone_number(phone_number=input_phone_number)
        if not phone_number:
            logger.info(f"{input_phone_number} is not valid")
            continue

        prefix = await request.app.state.get_prefix(request=request, phone_number=phone_number)
        if not prefix:
            logger.error(f"{phone_number} does not have a valid prefix")
            continue

        if prefix not in output:
            output[prefix] = {}
        sector = await get_sector(phone_number=phone_number)
        if sector not in output[prefix]:
            output[prefix][sector] = 0

        output[prefix][sector] += 1

    return JSONResponse(output, 200)
