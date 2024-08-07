import asyncio
import logging
import re

import aiohttp
from sqlalchemy.orm import sessionmaker

from models import BaseEngineSql, Vacancy
from nlp.interface_client import (
    client_api_text_to_tokens,
    client_api_text_to_tokens_async,
)
from settings_app import resume_text_path

log = logging.getLogger(__name__)


# Функция удаления часового пояса
def utc_to_local(utc_dt: str):
    return re.sub(r"\+.+", "", utc_dt)


def set_to_dict(obj: set) -> dict:
    return {key: None for key in obj}


class TokenizationResumeAndVacancies:
    """
    Токенизация резюме и вакансиями
    """

    @staticmethod
    def resume():
        """
        Токенизация резюме
        """

        def read_resume_text() -> str:
            """Получить текст вакансии из файла"""
            return resume_text_path.read_text(encoding="utf-8")

        return client_api_text_to_tokens(read_resume_text())

    @staticmethod
    def job_descriptions():
        """
        Токенизация текста вакансий
        """
        Session = sessionmaker(bind=BaseEngineSql)
        with Session() as session:
            job_descriptions = (
                session.query(Vacancy.id, Vacancy.description).filter(
                    # Открыта
                    # Vacancy.type_open == "open",
                    # Не откликался на вакансию
                    Vacancy.send_offer
                    == False,  # noqa E712
                )
            )

        job_descriptions = {job[0]: job[1] for job in job_descriptions}

        async def process_all():
            async with aiohttp.ClientSession() as session:
                tasks = [
                    client_api_text_to_tokens_async(description, session)
                    for description in job_descriptions.values()
                ]
                results = await asyncio.gather(*tasks)
            return {
                id_: tokens
                for (id_, _), tokens in zip(job_descriptions.items(), results)
            }

        return asyncio.run(process_all())
