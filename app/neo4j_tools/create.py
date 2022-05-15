from datetime import datetime

from app.neo4j_tools.neo4j_connection import get_driver


def get_attributes_string(**attributes) -> str:
    return '{' + ', '.join(f'{key}: "{value}"' for key, value in attributes.items() if value) + '}'


def do_cypher_create(tx, class_name, **attributes):
    """Вспомогательная функция для запуска Cypher-запроса на создание"""
    attributes_string = get_attributes_string(**attributes)
    tx.run(f'create (node:{class_name} {attributes_string});')


def create_node(class_name, **attributes):
    """Создает в Neo4j вершину с указанным классом и аттрибутами"""
    driver = get_driver()

    attributes['datetime_created'] = datetime.now()

    with driver.session() as session:
        session.write_transaction(do_cypher_create, class_name=class_name, **attributes)


def do_cypher_create_question(tx, form_id, **attributes):
    attributes_string = get_attributes_string(**attributes)
    tx.run(f'match (node:QuestionForm) where id(node)={form_id} create (node)-[:has_question]->(:Question {attributes_string});')


def create_question_for_form(form_id, **attributes):
    driver = get_driver()

    attributes['datetime_created'] = datetime.now()

    with driver.session() as session:
        session.write_transaction(do_cypher_create_question, form_id=form_id, **attributes)


def do_cypher_create_answer(tx, question_id, **attributes):
    attributes_string = get_attributes_string(**attributes)
    tx.run(f'match (node:Question) where id(node)={question_id} create (node)-[:has_answer]->(:Answer {attributes_string});')


def answer_for_question(question_id, **attributes):
    driver = get_driver()

    attributes['datetime_created'] = datetime.now()

    with driver.session() as session:
        session.write_transaction(do_cypher_create_answer, question_id=question_id, **attributes)
