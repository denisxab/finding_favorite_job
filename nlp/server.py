"""
python -m nlp.server
"""

from fastapi import FastAPI
from pydantic import BaseModel

from nlp.nltk_logic import CustomNltk

nltk_app = FastAPI()


nltk_processor = CustomNltk()


class TextInput(BaseModel):
    text: str


@nltk_app.post("/text_to_tokens")
async def text_to_tokens(input_data: TextInput):
    tokens = nltk_processor.text_to_tokens(input_data.text)
    return {"tokens": tokens}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("nlp.server:nltk_app", host="0.0.0.0", port=8932, workers=2)
