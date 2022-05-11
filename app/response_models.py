from datetime import datetime
from typing import List, Optional, Union
from pydantic import BaseModel

from app.constants import QuestionType


class Question(BaseModel):
    id: int
    text: str
    question_type: QuestionType
    datetime_created: datetime
    variants: Optional[List[str]] = None

    def __init__(__pydantic_self__, **data) -> None:
        variants: str = data['variants']
        variants = variants[1:-1].split(', ')
        data['variants'] = [v[1:-1] for v in variants]
        super().__init__(**data)


class QuestionForm(BaseModel):
    id: int
    name: str
    theme: str
    datetime_created: datetime
    questions: List[Question] = []


class AccountForms(BaseModel):
    forms: List[QuestionForm] = []
