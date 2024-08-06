import asyncio
import logging

import aiohttp
import requests


logger = logging.getLogger(__name__)


class ApiHH:
    @staticmethod
    def get_vacancies(salary, text, params_add, per_page=100, page=0):
        """Получить список вакансий по указанному фильтру

        https://api.hh.ru/openapi/redoc#tag/Poisk-vakansij/operation/get-vacancies
        https://api.hh.ru/openapi/redoc#tag/Obshie-spravochniki/operation/get-dictionaries
        """

        url = "https://api.hh.ru/vacancies"

        params = {
            "per_page": per_page,  # Количество вакансий на странице (максимум 100)
            "page": page,
            "text": text,  # Ваш поисковый запрос
            "salary": str(salary),
            **params_add,
        }

        response = requests.get(url, params=params)
        vacancies = response.json()
        return vacancies

    class FetchVacancies:
        """Получить текст вакансии по id"""

        def __init__(self):
            # Для хранения ошибок
            self.error_list: list[dict] = []

        async def fetch_vacancy(
            self, session, url, vacancy_id: int, max_retries=3, time_sleep=40
        ):
            """
            Функция для получения текста вакансии.

            Если ошибка от сервера(из за превышения количества запросов),
            то ждем time_sleep, и повторяем запрос до максимального количества попыток.
            """
            for attempt in range(max_retries):
                try:
                    async with session.get(url) as response:
                        res = await response.json()
                        if error := res.get("errors"):
                            logger.info(
                                f"Attempt {attempt + 1}: Errors fetch_vacancy: {error}"
                            )
                            if attempt < max_retries - 1:
                                logger.info(f"Retrying in {time_sleep} seconds...")
                                await asyncio.sleep(time_sleep)
                            else:
                                self.error_list.append({"id": vacancy_id})
                                logger.info(
                                    f"Max retries reached for vacancy {vacancy_id}"
                                )
                        else:
                            return res
                except Exception as e:
                    logger.info(f"Attempt {attempt + 1}: Exception occurred: {str(e)}")
                    if attempt < max_retries - 1:
                        logger.info(f"Retrying in {time_sleep} seconds...")
                        await asyncio.sleep(time_sleep)
                    else:
                        self.error_list.append({"id": vacancy_id})
                        logger.info(f"Max retries reached for vacancy {vacancy_id}")
            return None

        async def fetch_vacancies(self, vacancies_obj, count_get=3):
            response = []
            async with aiohttp.ClientSession() as session:
                tasks = []
                for i, v in enumerate(vacancies_obj):
                    vacancy_id = v["id"]
                    logger.info(f"Get {i} of {len(vacancies_obj)}")
                    vacancy_url = f"https://api.hh.ru/vacancies/{vacancy_id}"
                    tasks.append(
                        asyncio.create_task(
                            self.fetch_vacancy(session, vacancy_url, vacancy_id)
                        )
                    )
                    if len(tasks) == count_get or i == len(vacancies_obj) - 1:
                        results = await asyncio.gather(*tasks)
                        response.extend([r for r in results if r is not None])
                        tasks.clear()
            return response
