from enum import Enum


class QuestionType(str, Enum):
    text = 'text'
    radio = 'radio'
    checkbox = 'checkbox'
    number = 'number'
