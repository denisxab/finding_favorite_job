import asyncio
import logging
from typing import List

import aiohttp

from settings_app import url_nlp_server

logger = logging.getLogger(__name__)


def client_api_text_to_tokens(text: str) -> List[str]:
    async def run():
        async with aiohttp.ClientSession() as session:
            return await client_api_text_to_tokens_async(text, session)

    return asyncio.run(run())


async def client_api_text_to_tokens_async(
    text: str, session: aiohttp.ClientSession
) -> List[str]:
    payload = {"text": text}
    async with session.post(url_nlp_server, json=payload) as response:
        if response.status == 200:
            result = await response.json()
            return result["tokens"]
        else:
            logger.error(f"Ошибка: {response.status}")
            logger.error(await response.text())
            raise ValueError
