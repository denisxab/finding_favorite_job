from pathlib import Path
from typing import Final

base_path = Path(__file__).parent / "data"

vacancies_json_path: Final[Path] = base_path / "vacancies.json"
vacancies_text_json_path: Final[Path] = base_path / "vacancies_text.json"
vacancies_error_json_path: Final[Path] = base_path / "vacancies_error_text.json"
vacancies_db_path: Final[Path] = base_path / "vacancies.db"

resume_text_path: Final[Path] = base_path / "resume_text.md"

url_nlp_server: Final[str] = "http://localhost:8932/text_to_tokens"
