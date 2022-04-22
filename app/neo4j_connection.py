from datetime import datetime
from neo4j import GraphDatabase, Neo4jDriver

from app.config import neo4j_config


def get_driver() -> Neo4jDriver:
    """Возвращает драйвер подключения к Neo4j согласно настройкам в .env"""
    return GraphDatabase.driver(neo4j_config.uri, auth=(neo4j_config.username, neo4j_config.password))


def do_cypher_tx(tx, class_name, **attributes):
    """Вспомогательная функция для запуска Cypher-запроса"""
    attributes_string = '{' + ', '.join(f'{key}: "{value}"' for key, value in attributes.items()) + '}'
    return tx.run(f'create (node:{class_name} {attributes_string}) return node;')


def create_node(class_name, **attributes):
    """Создает в Neo4j вершину с указанным классом и аттрибутами"""
    driver = get_driver()

    attributes['datetime_created'] = datetime.now()

    with driver.session() as session:
        session.write_transaction(do_cypher_tx, class_name=class_name, **attributes)
