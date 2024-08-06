"""
Файл с API сервером получения и анализирования вакансий
"""

from fastapi import FastAPI, Query

from analytics import (
    ResponseFrequentSkills,
    ResponseSearch,
    find_out_the_statistics_of_frequent_skills,
    search_db_for_jobs_that_fit_my_resume,
)
from my_preferences import CURRENCY, SALARY, SCHEDULE, TARGET_TEXT_SEARCH
from receive_data import (
    converting_vacancies_by_db,
    get_job_text_from_hh_api,
    get_list_vacancies_from_hh_api,
    tokenize_vacancies_and_resumes_db,
)
import logging

app = FastAPI()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.post(
    "/get_by_api_hh_a_list_of_vacancies",
    tags=["API hh.ru"],
    summary="Получить по API hh.ru список вакансий.",
    description=f"""
    Получить по API hh.ru список вакансий.

    Документация API hh.ru

    - https://api.hh.ru/openapi/redoc#tag/Poisk-vakansij/operation/get-vacancies
    - https://api.hh.ru/openapi/redoc#tag/Obshie-spravochniki/operation/get-dictionaries

    Параметры поиска:

    SALARY = {SALARY}
    CURRENCY = {CURRENCY}
    SCHEDULE = {SCHEDULE}
    TARGET_TEXT_SEARCH = {TARGET_TEXT_SEARCH}
    """,
)
def api_get_by_api_hh_a_list_of_vacancies():
    get_list_vacancies_from_hh_api(
        SALARY,
        TARGET_TEXT_SEARCH,
        {
            "order_by": "publication_time",  # По дате публикации
            **({"schedule": SCHEDULE} if SCHEDULE else {}),
            **({"currency": CURRENCY} if CURRENCY else {}),
        },
    )
    return {"message": "OK"}


@app.post(
    "/get_by_api_hh_the_text_of_the_vacancy",
    tags=["API hh.ru"],
    summary="Получить по API hh.ru текст вакансий",
)
def api_get_by_api_hh_the_text_of_the_vacancy():
    """
    Получить по API hh.ru текст вакансий.
    """
    get_job_text_from_hh_api()
    converting_vacancies_by_db()
    tokenize_vacancies_and_resumes_db()
    return {"message": "OK"}


@app.get(
    "/search_db_for_jobs_that_fit_my_resume",
    tags=["Анализ данных"],
    summary="Поиск вакансий которые подходят под мое резюме",
)
def api_search_db_for_jobs_that_fit_my_resume(
    page: int = Query(default=0, description="Номер страницы"),
    page_count: int = Query(default=30, description="Сколько записей на странице"),
) -> list[ResponseSearch]:
    """
    Поиск вакансий которые подходят под мое резюме
    """
    return search_db_for_jobs_that_fit_my_resume(page, page_count)


@app.get(
    "/find_out_the_statistics_of_frequent_skills",
    tags=["Анализ данных"],
    summary="Узнать статистику частых скилов",
)
def api_find_out_the_statistics_of_frequent_skills(
    lang: str = Query(
        default="all",
        enum=["eng", "all"],
        description="Язык слов.",
    ),
    type_token: str = Query(
        default="missing_token",
        enum=["missing_token", "common_tokens"],
        description="""В каких токенах искать:

        - Которых у меня нет в резюме (type_token=missing_token)
        - Которые у меня есть в резюме (type_token=common_tokens)
        """,
    ),
) -> ResponseFrequentSkills:
    """Узнать статистику частых скилов в вакансиях"""
    return find_out_the_statistics_of_frequent_skills(
        lang,
        type_token,
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8912, reload=True)
