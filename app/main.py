from secrets import compare_digest
from fastapi import Depends, FastAPI, HTTPException, Response, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.neo4j_tools import create_node, edit_node
from app.neo4j_tools.create import create_question_for_form, create_token_authorization
from app.neo4j_tools.match_return import get_forms_by_username, get_node_by_id, get_questions_by_form_id, get_user_by_token, get_user_by_username

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


@app.post('/register/', name='Регистрация')
def register(body: UserWithPassword):
    """Создание пользователя с указанными логином и паролем."""
    create_node('User', **body.dict())
    token = create_token_authorization(body.username)
    
    return {'access_token': token, 'token_type': 'bearer'}


@app.post('/login/', name='Авторизация', response_model=Token)
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


QUESTION_FORM_URL = '/question-form'


@app.get(QUESTION_FORM_URL + '/all/', response_model=response_models.AccountForms, name='Опросники пользователя')
def get_user_question_forms(current_user: User = Depends(get_current_user)) -> response_models.AccountForms:
    """Выводит все опросники, которые создал пользователь"""
    question_forms = get_forms_by_username(current_user.username)

    return response_models.AccountForms(forms=[{**q['node'], 'id': q['node'].id} for q in question_forms])


@app.get(QUESTION_FORM_URL + '/{form_id}/', response_model=response_models.QuestionForm, name='Опросник')
def get_question_form(form_id: int, current_user: User = Depends(get_current_user)) -> response_models.QuestionForm:
    """Выводит подробную информацию об опроснике по id"""
    question_form = get_node_by_id('QuestionForm', form_id)
    if not question_form:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    question_form = question_form['node']
    questions = get_questions_by_form_id(form_id)

    questions = [{**q['node'], 'id': q['node'].id} for q in questions]

    return {**question_form, 'id': question_form.id, 'questions': questions}


@app.post(f'{QUESTION_FORM_URL}/create/', name='Новый опросник')
def create_empty_question_form(current_user: User = Depends(get_current_user)):
    """Создает пустой опросник"""
    create_node('QuestionForm', username=current_user.username, name='Пустая форма', theme='Нет темы')
    return Response(status_code=status.HTTP_201_CREATED)


@app.patch(QUESTION_FORM_URL + '/{form_id}/edit/', name='Редактировать опросник')
def edit_question_form(form_id: int, body: request_models.QuestionForm, current_user: User = Depends(get_current_user)):
    """Редактирование опросника"""
    edit_node('QuestionForm', node_id=form_id, **body.dict())
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.post(QUESTION_FORM_URL + '/{form_id}/questions/create/', name='Новый вопрос')
def create_empty_question(form_id: int, body: request_models.Question, current_user: User = Depends(get_current_user)):
    """Создает пустой вопрос"""
    create_question_for_form(form_id=form_id, **body.dict())
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.patch(QUESTION_FORM_URL + '/questions/{question_id}/edit/', name='Редактировать вопрос')
def edit_question(question_id: int, body: request_models.Question, current_user: User = Depends(get_current_user)):
    """Редактирование вопроса"""
    edit_node('Question', node_id=question_id, **body.dict())
    return Response(status_code=status.HTTP_204_NO_CONTENT)
