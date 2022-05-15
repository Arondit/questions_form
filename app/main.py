from secrets import compare_digest
import uuid
from fastapi import Depends, FastAPI, HTTPException, Response, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.constants import (
    QUESTION_FORM_URL,
    QUESTIONS_URL,
    AUTH_TAGS,
    QUESTION_FORM_TAGS,
    QUESTIONS_TAGS,
    ANSWERING_TAGS,
)
from app.neo4j_tools import create_node, edit_node
from app.neo4j_tools.auth import (
    create_token_authorization,
    get_user_by_token, 
    get_user_by_username,
)
from app.neo4j_tools.create import answer_for_question, create_question_for_form
from app.neo4j_tools.match_return import (
    get_form_by_code,
    get_forms_by_username, 
    get_node_by_id,
    get_question_answers, 
    get_questions_by_form_id,
)

import app.request_models as request_models
import app.response_models as response_models


app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


class User(BaseModel):
    username: str


class UserWithPassword(User):
    password: str


class Token(BaseModel):
    access_token: str 
    token_type: str


def get_current_user(token: str = Depends(oauth2_scheme)):
    user = get_user_by_token(token)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return User(username=user['node']['username'])


@app.get('/')
def main_page():
    """Главная страница"""
    return {'status': 'В разработке'}


@app.post('/register/', name='Регистрация', tags=AUTH_TAGS)
def register(body: UserWithPassword):
    """Создание пользователя с указанными логином и паролем."""
    create_node('User', **body.dict())
    token = create_token_authorization(body.username)
    
    return {'access_token': token, 'token_type': 'bearer'}


@app.post('/login/', name='Авторизация', response_model=Token, tags=AUTH_TAGS)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Создает в базе данных токен для пользователя и возвращает в ответе."""
    user = get_user_by_username(form_data.username)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    actual_password = user['node']['password']
    sent_password = form_data.password 
    
    if not compare_digest(str(actual_password), str(sent_password)):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    token = create_token_authorization(form_data.username)
    
    return {'access_token': token, 'token_type': 'bearer'}


@app.get(
    QUESTION_FORM_URL + '/all/', 
    response_model=response_models.AccountForms, 
    name='Опросники пользователя',
    tags=QUESTION_FORM_TAGS,
)
def get_user_question_forms(current_user: User = Depends(get_current_user)) -> response_models.AccountForms:
    """Выводит все опросники, которые создал пользователь"""
    question_forms = get_forms_by_username(current_user.username)

    return response_models.AccountForms(forms=[{**q['node'], 'id': q['node'].id} for q in question_forms])


@app.get(
    QUESTION_FORM_URL + '/{form_id}/', 
    response_model=response_models.QuestionForm, 
    name='Опросник', 
    tags=QUESTION_FORM_TAGS,
)
def get_question_form(form_id: int, current_user: User = Depends(get_current_user)) -> response_models.QuestionForm:
    """Выводит подробную информацию об опроснике по id"""
    question_form = get_node_by_id('QuestionForm', form_id)
    if not question_form:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    question_form = question_form['node']
    questions = get_questions_by_form_id(form_id)

    questions = [{**question['node'], 'id': question['node'].id} for question in questions]

    return {**question_form, 'id': question_form.id, 'questions': questions}


@app.post(f'{QUESTION_FORM_URL}/create/', name='Новый опросник', tags=QUESTION_FORM_TAGS)
def create_empty_question_form(current_user: User = Depends(get_current_user)):
    """Создает пустой опросник"""
    form_code = str(uuid.uuid4())[:8]
    create_node('QuestionForm', username=current_user.username, name='Пустая форма', theme='Нет темы', code=form_code)
    return Response(status_code=status.HTTP_201_CREATED)


@app.patch(QUESTION_FORM_URL + '/{form_id}/edit/', name='Редактировать опросник', tags=QUESTION_FORM_TAGS)
def edit_question_form(
    form_id: int, 
    body: request_models.QuestionForm, 
    current_user: User = Depends(get_current_user),
):
    """Редактирование опросника"""
    edit_node('QuestionForm', node_id=form_id, **body.dict())
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.post(QUESTION_FORM_URL + '/{form_id}/create-question/', name='Новый вопрос', tags=QUESTIONS_TAGS)
def create_empty_question(
    form_id: int, 
    body: request_models.Question, 
    current_user: User = Depends(get_current_user),
):
    """Создает пустой вопрос"""
    create_question_for_form(form_id=form_id, **body.dict())
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.patch(QUESTIONS_URL + '/{question_id}/edit/', name='Редактировать вопрос', tags=QUESTIONS_TAGS)
def edit_question(
    question_id: int, 
    body: request_models.Question, 
    current_user: User = Depends(get_current_user),
):
    """Редактирование вопроса"""
    edit_node('Question', node_id=question_id, **body.dict())
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.get(
    QUESTIONS_URL + '/{question_id}/answers/', 
    name='Ответы на вопрос', 
    response_model=response_models.QuestionResult,
    tags=QUESTIONS_TAGS,
)
def question_answers(question_id: int, current_user: User = Depends(get_current_user)):
    """Ответы на вопрос"""
    return get_question_answers(question_id)


@app.post(
    QUESTIONS_URL + '/{question_id}/answers/create', 
    name='Ответить на вопрос', 
    response_model=response_models.Answer,
    tags=ANSWERING_TAGS,
)
def answer_question(question_id: int, body: request_models.Answer):
    """Ответить на вопрос"""
    question = get_node_by_id('Question', node_id=question_id)
    if not question:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    question = question['node']
    correct_answer = question.get('correct_answer', None)
    
    if correct_answer is None:
        is_correct = None
    elif correct_answer == body.text:
        is_correct = True
    else:
        is_correct = False

    result = {'text': body.text, 'is_correct': is_correct, 'correct_answer': correct_answer}
    answer_for_question(question_id, **result)
    
    return result


@app.get(
    '/by-code/{form_code}/', 
    name='Пройти опрос', 
    response_model=response_models.QuestionForm, 
    tags=ANSWERING_TAGS,
)
def get_answer_form_for_answering(form_code: str):
    """Получает форму для прохождения опросника по коду"""
    question_form = get_form_by_code(form_code)
    if not question_form:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    question_form = question_form['node']
    questions = get_questions_by_form_id(question_form.id)

    questions = [{**question['node'], 'id': question['node'].id} for question in questions]

    return {**question_form, 'id': question_form.id, 'questions': questions}
