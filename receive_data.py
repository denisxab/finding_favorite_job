import asyncio
import json
import logging
from datetime import datetime
from sqlite3 import IntegrityError
from typing import Any

from markdownify import markdownify as md
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import sessionmaker

from models import BaseEngineSql, TokenizationVacancy, Vacancy
from requests_to_external_services import ApiHH
from settings_app import (
    vacancies_error_json_path,
    vacancies_json_path,
    vacancies_text_json_path,
)
from utils import TokenizationResumeAndVacancies, utc_to_local

logger = logging.getLogger(__name__)


def get_list_vacancies_from_hh_api(salary, text, params_add, per_page=100):
    """Получить список вакансий по указанному фильтру из API hh.ru

    params:
        - "currency": "RUR",
        - "order_by": "publication_time",  # По дате публикации
        - "schedule": "remote",  # Удаленная работа
    """

    response: list[dict[str, Any]] = []
    init_vacancies = ApiHH.get_vacancies(salary, text, params_add, per_page, page=0)
    response.extend(init_vacancies["items"])
    for page in range(1, init_vacancies["pages"]):
        logger.info(f"Page {page} of {init_vacancies['pages']}")
        vacancies = ApiHH.get_vacancies(salary, text, params_add, per_page, page)
        response.extend(vacancies["items"])

    # *Запись в файл
    vacancies_json_path.write_text(json.dumps(response, ensure_ascii=False, indent=2))
    logger.info("Success!: parse_list")


def get_job_text_from_hh_api():
    """Получить текст вакансии из API hh.ru"""
    vacancies_obj = None
    # *Если есть ошибки с загруженными вакансиями, то первым делом загрузим вакансии с ошибкой.
    if vacancies_error_json_path.exists():
        vacancies_obj = json.loads(vacancies_error_json_path.read_text())
        logger.info(f"loading error vacancies: {len(vacancies_obj)}")
    else:
        vacancies_obj = json.loads(vacancies_json_path.read_text())
        logger.info(f"loading vacancies: {len(vacancies_obj)}")

    # *Если такая вакансия уже есть в БД, то пропускаем такие вакансии.
    vacancies_obj_new = []
    Session = sessionmaker(bind=BaseEngineSql)
    with Session() as session:
        for vacancy in vacancies_obj:
            if not session.query(Vacancy).filter_by(id=vacancy["id"]).first():
                vacancies_obj_new.append(vacancy)
    vacancies_obj = vacancies_obj_new
    if not vacancies_obj:
        return True

    fv = ApiHH.FetchVacancies()
    response = asyncio.run(fv.fetch_vacancies(vacancies_obj))

    # *Запись в файл
    vacancies_text_json_path.write_text(
        json.dumps(response, ensure_ascii=False, indent=2)
    )
    if fv.error_list:
        # Сохраняем ошибки в файл, чтобы потом по ним попробовать снова
        vacancies_error_json_path.write_text(
            json.dumps(fv.error_list, ensure_ascii=False, indent=2)
        )
    else:
        # Если не было ошибок, то удалим файл
        vacancies_error_json_path.unlink(missing_ok=True)
    logger.info("Success!: get_vacancy_text")
    return False if fv.error_list else True


def converting_vacancies_by_db():
    """Преобразуем данные из файлов с вакансиями, в нужный формат для БД"""

    Session = sessionmaker(bind=BaseEngineSql)
    with Session() as session:
        # Преобразование JSON-данных в словарь Python
        for data in json.loads(vacancies_text_json_path.read_text()):
            # Если есть ошибки, то пропускаем итерацию
            if data.get("errors"):
                logger.warning(f"Error formatting_vacancies_text: {data.get('errors')}")
                continue
            # Извлечение необходимых данных из словаря
            experience = data.get("experience", {}).get("name", "")
            schedule = data.get("schedule", {}).get("name", "")
            employment = data.get("employment", {}).get("name", "")
            description = data.get("description", "")
            key_skills = [skill["name"] for skill in data.get("key_skills", [])]
            employer_id = data.get("employer", {}).get("id", None)
            employer_name = data.get("employer", {}).get("name", "")
            employer_url = data.get("employer", {}).get("url", "")
            published_at = datetime.fromisoformat(
                utc_to_local(data.get("published_at", ""))
            )
            created_at = datetime.fromisoformat(
                utc_to_local(data.get("created_at", ""))
            )
            initial_created_at = datetime.fromisoformat(
                utc_to_local(data.get("initial_created_at", ""))
            )

            salary_from = None
            salary_to = None
            salary_currency = None
            salary_gross = None

            type_open = data.get("type", {}).get("id", "")

            if data.get("salary"):
                salary_from = data.get("salary", {}).get("from", None)
                salary_to = data.get("salary", {}).get("to", None)
                salary_currency = data.get("salary", {}).get("currency", None)
                salary_gross = data.get("salary", {}).get("gross", None)

            description_text = md(description)

            # Проверка существования вакансии в базе данных
            vacancy = session.query(Vacancy).get(data["id"])

            if vacancy:
                # Обновление существующей записи
                vacancy.experience = experience
                vacancy.schedule = schedule
                vacancy.employment = employment
                vacancy.description = description_text
                vacancy.key_skills = (
                    json.dumps(key_skills, ensure_ascii=False) if key_skills else ""
                )
                vacancy.employer_id = employer_id
                vacancy.employer_name = employer_name
                vacancy.employer_url = employer_url
                vacancy.published_at = published_at
                vacancy.created_at = created_at
                vacancy.initial_created_at = initial_created_at
                vacancy.salary_from = salary_from
                vacancy.salary_to = salary_to
                vacancy.salary_currency = salary_currency
                vacancy.salary_gross = salary_gross
                vacancy.type_open = type_open

            else:
                # Создание новой записи
                vacancy = Vacancy(
                    id=data["id"],
                    experience=experience,
                    schedule=schedule,
                    employment=employment,
                    description=description_text,
                    key_skills=(
                        json.dumps(key_skills, ensure_ascii=False) if key_skills else ""
                    ),
                    employer_id=employer_id,
                    employer_name=employer_name,
                    employer_url=employer_url,
                    published_at=published_at,
                    created_at=created_at,
                    initial_created_at=initial_created_at,
                    salary_from=salary_from,
                    salary_to=salary_to,
                    salary_currency=salary_currency,
                    salary_gross=salary_gross,
                    type_open=type_open,
                )
                session.add(vacancy)

            # Сохранение изменений в базе данных
            try:
                session.commit()
            except IntegrityError:
                session.rollback()
                logger.error(f"Ошибка при сохранении вакансии с id {data['id']}")

    logger.info("Success!: formatting_vacancies_text")


def tokenize_vacancies_and_resumes_db():
    """
    Токенизация вакансий и резюме, для последующий сохранения в бд.
    """

    def save_response_to_db(response: TokenizationVacancy):
        """Сохранить ответ в базе данных или обновить, если он уже существует"""
        Session = sessionmaker(bind=BaseEngineSql)
        with Session() as session:
            try:
                # Попробуем найти существующую запись
                existing_response = (
                    session.query(TokenizationVacancy).filter_by(id=response.id).one()
                )
                # Если запись найдена, обновляем её
                existing_response.common_tokens = response.common_tokens
                existing_response.len_common_tokens = response.len_common_tokens
                existing_response.missing_tokens = response.missing_tokens
                existing_response.len_missing_tokens = response.len_missing_tokens
                existing_response.vacancy = response.vacancy
                existing_response.score = response.score
                logger.info(f"Response updated: {existing_response}")
            except NoResultFound:
                # Если запись не найдена, добавляем новую
                session.add(response)
                logger.warning(f"Response saved: {response}")
            session.commit()

    response: dict[int, TokenizationVacancy] = {}
    # Токенизация резюме
    resume_tokens = TokenizationResumeAndVacancies.resume()
    # Токенизация вакансий
    job_tokens: dict[int, str] = TokenizationResumeAndVacancies.job_descriptions()
    for id_, job in job_tokens.items():
        common_tokens: set = set(resume_tokens).intersection(set(job))
        missing_tokens: set = set(job) - set(resume_tokens)
        response[id_] = TokenizationVacancy(
            id=id_,
            common_tokens=json.dumps(
                list(common_tokens), ensure_ascii=False
            ),  # Преобразуем в строку
            len_common_tokens=len(common_tokens),
            vacancy=str(job),  # Преобразуем в строку
            missing_tokens=json.dumps(
                list(missing_tokens), ensure_ascii=False
            ),  # Преобразуем в строку
            len_missing_tokens=len(missing_tokens),
            score=0.0,
        )
        score = len(common_tokens) / len(job) if job else 0
        response[id_].score = float(f"{score:.2f}")
        # Сохраняем ответ в БД
        save_response_to_db(response[id_])

    logger.info("Success!: find_similar_vacancies")
