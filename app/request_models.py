from typing import List, Optional
from pydantic import BaseModel

from app.constants import QuestionType


class Question(BaseModel):
    text: str
    question_type: QuestionType = QuestionType.text.name
    variants: Optional[List[str]] = None


class QuestionForm(BaseModel):
    name: Optional[str] = None
    username: Optional[str] = None
    theme: Optional[str] = None
    is_quiz: Optional[bool] = None
