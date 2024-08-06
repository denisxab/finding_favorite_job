"""
Файл где указываются ваши предпочтения
"""

from dataclasses import dataclass
from typing import Literal

# Зарплата от в рублях
SALARY = 200_000
# Валюта
CURRENCY = "RUR"
# График работы
SCHEDULE: Literal["full_time", "remote", "part_time"] = "remote"
# Текст поискового запроса
TARGET_TEXT_SEARCH = {
    "python_detail": """NAME:((python OR python backend OR python django OR django OR DRF OR python fastapi OR python медицина) AND (NOT QA NOT тестировщик NOT fullstack NOT "Full Stack")) DESCRIPTION:(python OR django OR fastapi OR drf OR rest api OR медицина)""",
    "python_all": "python OR python backend OR python django OR django OR DRF OR python fastapi OR python медицина",
}["python_detail"]


class PreferencePoints:
    """
    Ваши предпочтения по вакансиям, выраженные в баллах.

    ! Помните что слова и предложения нужно писать из токенов, а не из целых слов !

    Эти очки будут учитываться для подбора вакансий для вашего резюме

    Например это используется в:

    - http://HOST/search_db_for_jobs_that_fit_my_resume
    """

    # Предпочтения и отрицания по словам в тексте вакансии
    SCORE_LIKE: dict[str, float | int] = {
        #
        # Предпочтения по фреймворкам
        "django": 2,
        "fastapi": 1,
        "gin": 2,
        "gorm": 2,
        "go": 1,
        "golang": 1,
        "jenkin": 1,
        #
        # Предпочтения по БД
        "postgresql": 0.2,
        "mysql": -0.2,
        "oracl": -0.2,
        #
        # Другие не предпочтительные технологии
        "airflow": -0.2,
        "java": -1,
        #
        # Ваши красные флаги для вакансий
        "печеньк": -100,
        "кофе": -100,
    }

    @dataclass
    class ScoreLikePhraseClass:
        phrase: list[list[str]]
        score: float | int

    # Предпочтения и отрицания по словосочетаниям в тексте вакансии
    SCORE_LIKE_PHRASE: list[ScoreLikePhraseClass] = [
        # Отдаляем вакансии с упоминание про высшие образование
        ScoreLikePhraseClass(
            phrase=[
                ["высш", "техническ", "образован"],
                ["высш", "образован"],
                ["инженерн", "техническ", "образован"],
            ],
            score=-100,
        ),
        # Отдаляем вакансии с упоминание про знание устного английского языка
        ScoreLikePhraseClass(
            phrase=[
                ["уровен", "английск", "от", "b1"],
            ],
            score=-100,
        ),
        # То что не относится к моей вакансии
        ScoreLikePhraseClass(
            phrase=[
                ["оп", "работ", "в", "рол", "team", "lead", "от"],
            ],
            score=-100,
        ),
    ]
