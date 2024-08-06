from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    Integer,
    String,
    Text,
    create_engine,
)
from sqlalchemy.ext.declarative import declarative_base

from settings_app import vacancies_db_path

Base = declarative_base()


class Vacancy(Base):
    __tablename__ = "vacancies"

    id = Column(Integer, primary_key=True)
    experience = Column(String(50))  # Опыт работы
    schedule = Column(String(50))  # График работы
    employment = Column(String(50))  # Тип занятости
    description = Column(Text)  # Описание вакансии
    key_skills = Column(Text)  # Ключевые навыки (в формате JSON)
    employer_id = Column(Integer)  # ID работодателя
    employer_name = Column(String(100))  # Имя работодателя
    employer_url = Column(String(200))  # URL работодателя
    published_at = Column(DateTime)  # Дата публикации
    created_at = Column(DateTime)  # Дата создания
    initial_created_at = Column(DateTime)  # Дата первоначального создания

    salary_from = Column(Integer)  # ЗП от
    salary_to = Column(Integer)  # ЗП до
    salary_currency = Column(Text)  # валюта ЗП
    salary_gross = Column(Boolean)  # 1 - значит без учета налогов, 0 - на ручки
    type_open = Column(Text)  # Открыта ли вакансия
    # Откликнулся ли я на вакансию(заполнять вручную)
    send_offer = Column(Boolean, default=False)


class TokenizationVacancy(Base):
    __tablename__ = "tokenization"

    id = Column(Integer, primary_key=True)
    common_tokens = Column(Text)  # Общие токены
    len_common_tokens = Column(Integer)  # Количество общих токенов
    missing_tokens = Column(Text)  # Отсутствующие токены
    len_missing_tokens = Column(Integer)  # Количество отсутствующих токенов
    vacancy = Column(Text)  # Вакансия
    score = Column(Float)  # Оценка


# Создание базы данных и таблицы
BaseEngineSql = create_engine(f"sqlite:///{vacancies_db_path}")
Base.metadata.create_all(BaseEngineSql)
