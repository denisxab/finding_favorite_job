import json
import logging
import re
from dataclasses import dataclass

from sqlalchemy.orm import sessionmaker

from models import BaseEngineSql, TokenizationVacancy
from my_preferences import PreferencePoints
from receive_data import TokenizationResumeAndVacancies

logger = logging.getLogger(__name__)


@dataclass
class ResponseSearch:
    vacancy_id: int
    score: float
    score_preference: float
    common_tokens: str
    missing_tokens: str
    job: str
    job_text: str


def search_db_for_jobs_that_fit_my_resume(limit: int = 100) -> list[ResponseSearch]:
    """Поиск вакансий которые подходят под мое резюме."""

    resume_tokens = TokenizationResumeAndVacancies.resume()
    (
        job_descriptions_tokens,
        job_descriptions,
    ) = TokenizationResumeAndVacancies.job_descriptions()

    response = []
    for id_, job in job_descriptions_tokens.items():
        common_tokens: set = set(resume_tokens).intersection(set(job))
        missing_tokens: set = set(job) - set(resume_tokens)
        score = len(common_tokens) / len(job) if job else 0
        score_preference: float = score

        # Прибавляем или отнимаем баллы по предпочтениям словам
        for token in job:
            if score_word := PreferencePoints.SCORE_LIKE.get(token):
                score_preference += float(score_word)

        # Прибавляем или отнимаем баллы по предпочтениям словосочетаниям
        job_str = ",".join(map(str, job))
        for phrases in PreferencePoints.SCORE_LIKE_PHRASE:
            for phrase in phrases.phrase:
                # Преобразуем списки в строки
                sub_str = ",".join(map(str, phrase))
                # Поиск подстроки в строке
                if sub_str in job_str:
                    score_preference += float(phrases.score)

        response.append(
            ResponseSearch(
                vacancy_id=id_,
                score=score,
                score_preference=score_preference,
                common_tokens=json.dumps(list(common_tokens), ensure_ascii=False),
                missing_tokens=json.dumps(list(missing_tokens), ensure_ascii=False),
                job=json.dumps(list(job), ensure_ascii=False),
                job_text=job_descriptions[id_],
            )
        )
    sort_response = sorted(response, key=lambda x: x.score_preference, reverse=True)

    if limit > 0:
        return sort_response[:limit]
    else:
        return sort_response


@dataclass
class SortedTokensCount:
    name: str
    count: int
    count_p: float


@dataclass
class ResponseFrequentSkills:
    type_token: str
    all_count: int
    message: list[SortedTokensCount]


def find_out_the_statistics_of_frequent_skills(lang: str, type_token: str):
    """
    Статистика частых скилов в вакансиях:

    - Которых у есть в резюме (type_token=common_tokens)
    - Которых у меня нет в резюме (type_token=missing_token)
    """

    tokens_count: dict[str, int] = {}
    all_count = 0

    Session = sessionmaker(bind=BaseEngineSql)
    with Session() as session:
        rows = session.query(TokenizationVacancy).all()
        for row in rows:
            if type_token == "common_tokens":
                if not row.common_tokens:
                    continue
                common_tokens_row = json.loads(row.common_tokens)
                for m in common_tokens_row:
                    tokens_count[m] = tokens_count.get(m, 0) + 1
            elif type_token == "missing_token":
                if not row.missing_tokens:
                    continue
                missing_token_row = json.loads(row.missing_tokens)
                for m in missing_token_row:
                    tokens_count[m] = tokens_count.get(m, 0) + 1
            all_count += 1

    # Отсортировать missing_tokens_count
    sorted_tokens_count = sorted(tokens_count.items(), key=lambda x: x[1], reverse=True)
    message = []
    if lang == "eng":
        # Только слова на английском
        message = [
            SortedTokensCount(
                name=k,
                count=v,
                count_p=round((v / all_count) * 100, 2),
            )
            for k, v in sorted_tokens_count
            if re.match(r"[a-zA-Z]", k)
        ]
    else:
        message = [
            SortedTokensCount(
                name=k,
                count=v,
                count_p=round((v / all_count) * 100, 2),
            )
            for k, v in sorted_tokens_count
        ]

    return ResponseFrequentSkills(
        type_token=type_token,
        all_count=all_count,
        message=message[:200],
    )
