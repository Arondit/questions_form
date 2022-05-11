from datetime import datetime
import uuid

from app.neo4j_tools.neo4j_connection import get_driver


def do_cypher_create(tx, class_name, **attributes):
    """Вспомогательная функция для запуска Cypher-запроса на создание"""
    attributes_string = '{' + ', '.join(f'{key}: "{value}"' for key, value in attributes.items() if value) + '}'
    tx.run(f'create (node:{class_name} {attributes_string});')


def create_node(class_name, **attributes):
    """Создает в Neo4j вершину с указанным классом и аттрибутами"""
    driver = get_driver()

    attributes['datetime_created'] = datetime.now()

    with driver.session() as session:
        session.write_transaction(do_cypher_create, class_name=class_name, **attributes)


def do_cypher_create_question(tx, form_id, **attributes):
    attributes_string = '{' + ', '.join(f'{key}: "{value}"' for key, value in attributes.items() if value) + '}'
    tx.run(f'match (node:QuestionForm) where id(node)={form_id} create (node)-[:has_question]->(:Question {attributes_string});')


def create_question_for_form(form_id, **attributes):
    driver = get_driver()

    attributes['datetime_created'] = datetime.now()

    with driver.session() as session:
        session.write_transaction(do_cypher_create_question, form_id=form_id, **attributes)


def do_cypher_create_token(tx, username, token):
    """Вспомогательная функция для добавления в базу токена авторизации"""
    attributes = {'datetime_created': datetime.now(), 'token': token}
    attributes_string = '{' + ', '.join(f'{key}: "{value}"' for key, value in attributes.items() if value) + '}'
    tx.run(f'match (user:User) where user.username="{username}" create (:Token {attributes_string})-[:authenticate]->(user);')


def create_token_authorization(username):
    """Создает в Neo4j вершину токена, которая указывает на пользователя"""
    driver = get_driver()

    token = str(uuid.uuid4())

    with driver.session() as session:
        session.write_transaction(do_cypher_create_token, username=username, token=token)
    
    return token
