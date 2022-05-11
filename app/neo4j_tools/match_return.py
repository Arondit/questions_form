from app.neo4j_tools.neo4j_connection import get_driver


def do_cypher_get(tx, class_name, node_id):
    """Вспомогательная функция для запуска Cypher-запроса на чтение"""
    return list(tx.run(f'match (node:{class_name}) where id(node)={node_id} return node;'))


def get_node_by_id(class_name, node_id):
    """Получает из Neo4j вершину с указанным классом и id"""
    driver = get_driver()

    with driver.session() as session:
        result = session.read_transaction(do_cypher_get, class_name=class_name, node_id=node_id)
        return result[0] if result else result


def do_cypher_get_forms_by_username(tx, username):
    """Вспомогательная функция для запуска Cypher-запроса на чтение"""
    return list(tx.run(f'match (node:QuestionForm) where node.username="{username}" return node;'))


def get_forms_by_username(username):
    driver = get_driver()

    with driver.session() as session:
        return session.read_transaction(do_cypher_get_forms_by_username, username=username)


def do_cypher_get_questions_by_form_id(tx, form_id):
    """Вспомогательная функция для запуска Cypher-запроса на чтение"""
    match_part = f'match (question_form:QuestionForm)-[:has_question]->(node:Question) '
    rest_part = f'where id(question_form)={form_id} return node;'
    return list(tx.run(match_part + rest_part))


def get_questions_by_form_id(form_id):
    driver = get_driver()

    with driver.session() as session:
        return session.read_transaction(do_cypher_get_questions_by_form_id, form_id=form_id)


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
