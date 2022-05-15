from enum import Enum


class QuestionType(str, Enum):
    text = 'text'
    radio = 'radio'
    checkbox = 'checkbox'


QUESTION_FORM_URL = '/question-form'
QUESTIONS_URL = f'{QUESTION_FORM_URL}/questions'


AUTH_TAGS = ['Регистрация/Авторизация']
QUESTION_FORM_TAGS = ['Опросники']
QUESTIONS_TAGS = ['Вопросы']
ANSWERS_TAGS = ['Ответы']
ANSWERING_TAGS = ['Прохождение опроса']
