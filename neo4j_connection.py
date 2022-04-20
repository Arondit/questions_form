from neo4j import GraphDatabase

from config import neo4j_config


def get_driver():
    """Возвращает драйвер подключения к Neo4j согласно настройкам в .env"""
    return GraphDatabase.driver(neo4j_config.uri, auth=(neo4j_config.username, neo4j_config.password))


def do_cypher_tx(tx, cypher):
    """Вспомогательная функция для запуска Cypher-запроса"""
    tx.run(cypher)


def create_node(class_name, **attributes):
    """Создает в Neo4j вершину с указанным классом и аттрибутами"""
    driver = get_driver()
    attributes_string = '{' + ', '.join(f'{key}: "{value}"' for key, value in attributes.items()) + '}'

    with driver.session() as session:
        values = session.write_transaction(do_cypher_tx, f'create (:{class_name} {attributes_string})')
    driver.close()

    return values
