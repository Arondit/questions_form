from fastapi import FastAPI

from app.config import app_config
from app.neo4j_connection import create_node


app = FastAPI()


urls_base = {
    'question_form': '/question-form/',
}


@app.get('/')
def main_page():
    """Главная страница"""
    return {'status': 'В разработке'}


@app.post('/question-form/create')
def create_empty_question_form():
    """Создает пустой опросник"""
    create_node('QuestionForm', author_name='Vlad')
    return {'some_field': 'success'}


@app.get('/test/env')
def is_heroku():
    """Корректно ли работает env конфиг в связке с Heroku"""
    return {'is_heroku': app_config.IS_HEROKU}
