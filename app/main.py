from fastapi import FastAPI


app = FastAPI()


@app.get('/')
def main_apge():
    """Главная страница"""
    return {'status': 'В разработке'}


@app.post('/question-form/create')
def create_empty_question_form():
    """Создает пустой опросник"""
    return {'some_field': 'success'}
