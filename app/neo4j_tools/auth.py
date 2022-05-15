from datetime import datetime
import uuid
from app.neo4j_tools.neo4j_connection import get_driver


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


def do_cypher_get_user_by_username(tx, username):
    """Вспомогательная функция для запуска Cypher-запроса на чтение"""
    return list(tx.run(f'match (node:User) where node.username="{username}" return node;'))


def get_user_by_username(username):
    driver = get_driver()

    with driver.session() as session:
        result = session.read_transaction(do_cypher_get_user_by_username, username=username)
        return result[0] if result else result


def do_cypher_get_user_by_token(tx, token):
    """Вспомогательная функция для запуска Cypher-запроса на чтение"""
    return list(tx.run(f'match (token:Token)-[authenticate]->(node:User) where token.token="{token}" return node;'))


def get_user_by_token(token):
    driver = get_driver()

    with driver.session() as session:
        result = session.read_transaction(do_cypher_get_user_by_token, token=token)
        return result[0] if result else result
