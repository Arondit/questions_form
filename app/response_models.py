from datetime import datetime
from typing import List, Optional, Dict
from pydantic import BaseModel

from app.constants import QuestionType


class Question(BaseModel):
    id: int
    text: str
    question_type: QuestionType
    datetime_created: datetime
    variants: Optional[List[str]] = None
    correct_answer: Optional[str] = None

    def __init__(__pydantic_self__, **data) -> None:
        variants: str = data['variants']
        variants = variants[1:-1].split(', ')
        data['variants'] = [v[1:-1] for v in variants]
        super().__init__(**data)


class QuestionForm(BaseModel):
    id: int
    name: str
    theme: str
    code: str
    datetime_created: datetime
    is_quiz: Optional[bool] = None
    questions: List[Question] = []


class AccountForms(BaseModel):
    forms: List[QuestionForm] = []


class Answer(BaseModel):
    text: str
    is_correct: Optional[bool] = None
    correct_answer: Optional[str] = None


class QuestionResult(BaseModel):
    answers: Dict[str, int]
    all_answers_count: int
    correct_answers_count: int
