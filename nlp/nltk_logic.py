import re

import nltk
from nltk.stem import SnowballStemmer
from nltk.tokenize import word_tokenize


class CustomNltk:
    """Кастомный нлп"""

    def __init__(self):
        nltk.download("punkt")

        # Инициализация стеммеров
        self.russian_stemmer = SnowballStemmer("russian")
        self.english_stemmer = SnowballStemmer("english")

    def text_to_tokens(self, text: str) -> list[str]:
        """
        Токенизация текста
        """
        return self._stem_tokens(word_tokenize(self._clean_text(text.lower())))

    def _stem_tokens(self, tokens):
        """Стемминг токенов для русского и английского языков

        Стемминг — это процесс, который уменьшает слова до их основы или корня.
        В отличие от лемматизации, стемминг не обязательно возвращает слово к его правильной лексической форме,
        а просто отсекает окончания.
        """
        stemmed_tokens = []
        for token in tokens:
            # Проверка, является ли токен числом
            if re.match(r"^\d+$", token):
                stemmed_tokens.append(token)  # Возвращаем число без изменений
            # Проверка языка
            elif re.match(r"[а-яА-ЯёЁ]", token):
                stemmed_tokens.append(
                    self.russian_stemmer.stem(token)
                )  # Стемминг для русского
            elif re.match(r"[a-zA-Z]", token):
                stemmed_tokens.append(
                    self.english_stemmer.stem(token)
                )  # Стемминг для английского
            else:
                stemmed_tokens.append(
                    token
                )  # Возвращаем токен без изменений, если язык не распознан
        return stemmed_tokens

    @staticmethod
    def _clean_text(text):
        # Используем регулярное выражение для удаления всего, кроме букв и цифр
        cleaned_text = re.sub(r"[^a-zA-Zа-яА-ЯёЁ0-9]", " ", text)
        # Удаляем лишние пробелы
        cleaned_text = re.sub(r"\s+", " ", cleaned_text).strip()
        return cleaned_text
