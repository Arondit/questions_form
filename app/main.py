from fastapi import FastAPI

from app.config import AppConfig


app = FastAPI()


@app.get('/')
def main_apge():
    """Главная страница"""
    return {'status': 'В разработке'}


@app.post('/question-form/create')
def create_empty_question_form():
    """Создает пустой опросник"""
    return {'some_field': 'success'}


@app.get('/test/env')
def is_heroku():
    """Корректно ли работает env конфиг в связке с Heroku"""
    return {'is_heroku': AppConfig.IS_HEROKU}
