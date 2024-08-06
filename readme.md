# Как я разработал собственную рекомендательную систему вакансий и почему вам это тоже может пригодиться

## Введение

Недавно, просматривая рекомендации на популярном сайте поиска работы по моему резюме "Senior Python backend", я заметил, что система предлагает вакансии, весьма далекие от моей специализации. Это натолкнуло меня на размышления о том, как можно улучшить процесс подбора вакансий для IT-специалистов. В результате я решил создать свою собственную рекомендательную систему, которая бы более точно учитывала специфику работы в сфере разработки программного обеспечения.

## Целевая аудитория

Эта статья предназначена для backend-разработчиков, ищущих работу на hh.ru. Если вы действительно компетентный специалист, то сможете разобраться с этим спартанским(неудобным) интерфейсом. Высокий порог входа – не следствие моей лени, а намеренное решение проверить ваши навыки.

## Концепция системы

Моя система работает в три этапа:

1. Получение списка вакансий по заданному фильтру через API сайта поиска работы с последующим сохранением в базу данных.
2. Получение полного текста каждой вакансии через API hh.ru и сохранение в БД.
3. Анализ локально хранящихся данных различными способами.

## Алгоритм поиска подходящих вакансий

Разработанный алгоритм для поиска вакансий, наиболее соответствующих вашему резюме, включает следующие ключевые этапы:

1. **Предварительная обработка текста:**

    - Токенизация текста резюме и описаний вакансий.
    - Удаление стоп-слов и пунктуации.
    - Лемматизация или стемминг для приведения слов к базовой форме.

2. **Анализ соответствия:**

    - Определение процента соответствия между резюме и каждой вакансией;

3. **Фильтрация результатов:**

    - Исключение вакансий с нежелательными ключевыми словами или фразами. Например:
        - "печеньки" (если вы не заинтересованы в неформальной корпоративной культуре)
        - "работа-семья" (если вы ищете строго профессиональную среду)
        - "высшее техническое образование" (если у вас другой профиль образования)

4. **Персонализированная сортировка:**

    - Возможность задать предпочтительные технологии или условия работы.
    - Присвоение дополнительных баллов вакансиям, содержащим предпочтительные элементы. Например, если вы предпочитаете Postgres вместо MySQL, вакансии с упоминанием Postgres получат более высокий рейтинг.

5. **Динамическая настройка:**

    - Возможность изменять веса различных факторов в алгоритме ранжирования.
    - Опция для добавления новых критериев или изменения существующих без необходимости переписывать весь алгоритм.

6. **Визуализация результатов:**
    - Представление результатов в виде отсортированного списка вакансий с указанием процента соответствия и ключевых совпадений.
    - Опция для детального просмотра, показывающая, какие именно факторы повлияли на рейтинг каждой вакансии.

Этот алгоритм позволяет не только находить наиболее релевантные вакансии, но и тонко настраивать поиск под индивидуальные предпочтения и карьерные цели.

Система также позволяет:

-   Выявлять наиболее часто встречающиеся технологии для потенциального изучения и добавления в резюме.
-   Обнаруживать новые технологии, набирающие популярность, но пока не очевидные на первый взгляд.

## Инструкция по использованию

1. Настройте файл `my_preferences.py` под свои требования.
2. Создайте файл `data/resume_text.md` и сохраните в него текст вашего резюме. Формат текста не имеет значения – система будет искать совпадения по словам или предложениям.
3. Запустите основной сервер:

```bash
python main.py
```

4. Запустите сервер обработки текста (вынесен отдельно из-за длительной загрузки модели `nltk`):

```bash
python -m nlp.server
```

5. Откройте документацию API по адресу `http://localhost:8912/docs#/`

## Интерпретация результатов API

### `/search_db_for_jobs_that_fit_my_resume`

```jsonc
[
    {
        "vacancy_id": 0, // ID вакансии (для просмотра на HH.ru: https://spb.hh.ru/vacancy/{vacancy_id})
        "score": 0, // Очки совпадения без учета личных предпочтений
        "score_preference": 0, // Очки совпадения с учетом личных предпочтений
        "common_tokens": "string", // Совпавшие с резюме токены (без учета порядка)
        "missing_tokens": "string", // Несовпавшие с резюме токены (без учета порядка)
        "job": "string" // Токенизированный текст вакансии (с учетом порядка)
    }
]
```

Результаты сортируются по полю `score_preference`.

### `/find_out_the_statistics_of_frequent_skills`

```jsonc
{
    "type_token": "string",
    "all_count": 0, // Общее количество уникальных слов
    "message": [
        {
            "name": "string", // Слово
            "count": 0, // Частота встречаемости во всех вакансиях
            "count_p": 0 // Процентное соотношение частоты
        }
    ]
}
```

## Заключение

Разработка собственной рекомендательной системы вакансий может значительно повысить эффективность поиска работы, особенно для опытных разработчиков. Надеюсь, мой опыт вдохновит вас на создание собственных инструментов для оптимизации процесса трудоустройства.

Код проекта доступен на GitHub: https://github.com/denisxab/finding_favorite_job

Буду рад вашим комментариям и предложениям по улучшению системы!

# API hh.ru - Поиск и фильтрация списка вакансий

-   https://api.hh.ru/openapi/redoc#tag/Poisk-vakansij/operation/get-vacancies
-   https://api.hh.ru/openapi/redoc#tag/Obshie-spravochniki/operation/get-dictionaries

Позволяет использовать различные параметры для поиска вакансий. Вот основные параметры, которые можно отправлять в запросе к эндпоинту "https://api.hh.ru/vacancies":

-   `text`: строка для поиска вакансий по ключевым словам.
-   `area`: код региона (например, 1 для Москвы).
-   `specialization`: код специализации (например, IT).
-   `employment`: тип занятости (например, full для полной занятости).
-   `schedule`: график работы (например, fullDay для полного дня).
-   `experience`: опыт работы (например, between1And3 для опыта от 1 до 3 лет).
-   `salary`: зарплата (например, от 50000).
-   `currency`: валюта зарплаты (например, RUR).
-   `page`: номер страницы (для пагинации).
-   `per_page`: количество вакансий на странице (максимум 100).
-   `order_by`: сортировка (например, publication_time для сортировки по времени публикации).
-   `only_with_salary`: только вакансии с указанной зарплатой (true или false).
-   `period`: период публикации вакансий (например, 30 для последних 30 дней).
-   `employer_id`: ID работодателя для фильтрации вакансий по конкретному работодателю.
-   `industry`: код индустрии (например, 7 для IT).

Пример запроса с параметрами:

```python
import requests

url = "https://api.hh.ru/vacancies"
params = {
    "text": "Python разработчик",
    "area": 1,
    "employment": "full",
    "experience": "between1And3",
    "salary": 500_000,
    "currency": "RUR",
    "page": 0,
    "per_page": 20
}

response = requests.get(url, params=params)
vacancies = response.json()
```

Этот запрос вернет список вакансий для Python разработчиков в Москве с полной занятостью и опытом работы от 1 до 3 лет, с зарплатой от 500_000 рублей в месяц.

# SQl запросы

-   Получить список наиболее частых ключевых навыков

```sql
WITH RECURSIVE
  split(skill, rest) AS (
    SELECT '', key_skills || ',' FROM vacancies WHERE key_skills != ''
    UNION ALL
    SELECT
      substr(rest, 0, instr(rest, ',')),
      substr(rest, instr(rest, ',') + 1)
    FROM split
    WHERE rest != ''
  ),
  counted_skills AS (
    SELECT
      t.skill,
      COUNT(*) as count
    FROM (
      SELECT
        REPLACE(REPLACE(trim(skill), '[', ''), ']', '') as skill
      FROM split
      WHERE skill != ''
    ) t
    WHERE skill != ''
    GROUP BY skill
    HAVING COUNT(*) > 3
  )

SELECT
  skill,
  count,
  ROUND(count * 100.0 / SUM(count) OVER(), 2) AS percentage
FROM counted_skills
ORDER BY count DESC, skill
```

-   Получить вакансии самой большой ЗП

```sql
SELECT
	*
	--v.id,v.description,v.employer_name,v.salary_from, salary_to
from vacancies v
where
	v.salary_from is not null
	and v.salary_currency = 'RUR'
	-- and v.salary_gross = 0
order by v.salary_from desc, salary_to desc
```

-   Получить список наиболее подходящих вакансий

```sql
select v.employer_name, v.description, r.score, r.* from tokenization r
join vacancies v on v.id = r.id
order by r.score desc
```

-   Узнать частые скилы которых у меня нет в резюме

```sql
WITH RECURSIVE
  split(skill, rest) AS (
    SELECT '', missing_tokens || ',' FROM tokenization WHERE missing_tokens != ''
    UNION ALL
    SELECT
      substr(rest, 0, instr(rest, ',')),
      substr(rest, instr(rest, ',') + 1)
    FROM split
    WHERE rest != ''
  ),
  counted_skills AS (
    SELECT
      t.skill,
      COUNT(*) as count
    FROM (
      SELECT
        REPLACE(REPLACE(trim(skill), '{', ''), '}', '') as skill
      FROM split
      WHERE skill != ''
    ) t
    WHERE skill != ''
    GROUP BY skill
    HAVING COUNT(*) > 3
  )

SELECT
  skill,
  count,
  ROUND(count * 100.0 / SUM(count) OVER(), 2) AS percentage
FROM counted_skills
ORDER BY count DESC, skill
```
