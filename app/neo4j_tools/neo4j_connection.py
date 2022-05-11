from neo4j import GraphDatabase, Neo4jDriver

from app.config import neo4j_config


def get_driver() -> Neo4jDriver:
    """Возвращает драйвер подключения к Neo4j согласно настройкам в .env"""
    return GraphDatabase.driver(neo4j_config.uri, auth=(neo4j_config.username, neo4j_config.password))
