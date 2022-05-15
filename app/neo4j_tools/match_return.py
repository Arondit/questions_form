from collections import Counter
from app.neo4j_tools.neo4j_connection import get_driver


def do_cypher_get(tx, class_name: str, node_id: int):
    """Вспомогательная функция для запуска Cypher-запроса на чтение"""
    return list(tx.run(f'match (node:{class_name}) where id(node)={node_id} return node;'))


def get_node_by_id(class_name: str, node_id: int):
    """Получает из Neo4j вершину с указанным классом и id"""
    driver = get_driver()

    with driver.session() as session:
        result = session.read_transaction(do_cypher_get, class_name=class_name, node_id=node_id)
        return result[0] if result else result


def do_cypher_get_forms_by_username(tx, username: str):
    """Вспомогательная функция для запуска Cypher-запроса на чтение"""
    return list(tx.run(f'match (node:QuestionForm) where node.username="{username}" return node;'))


def get_forms_by_username(username: str):
    driver = get_driver()

    with driver.session() as session:
        return session.read_transaction(do_cypher_get_forms_by_username, username=username)


def do_cypher_get_questions_by_form_id(tx, form_id: int):
    """Вспомогательная функция для запуска Cypher-запроса на чтение"""
    match_part = 'match (question_form:QuestionForm)-[:has_question]->(node:Question) '
    rest_part = f'where id(question_form)={form_id} return node;'
    return list(tx.run(match_part + rest_part))


def get_questions_by_form_id(form_id: int):
    driver = get_driver()

    with driver.session() as session:
        return session.read_transaction(do_cypher_get_questions_by_form_id, form_id=form_id)


def do_cypher_get_question_answers(tx, question_id: int):
    """Вспомогательная функция для запуска Cypher-запроса на чтение"""
    match_part = f'match (question:Question)-[:has_answer]->(node:Answer) '
    rest_part = f'where id(question)={question_id} return node;'
    return list(tx.run(match_part + rest_part))


def get_question_answers(question_id: int):
    """"""
    driver = get_driver()

    with driver.session() as session:
        answers = session.read_transaction(do_cypher_get_question_answers, question_id=question_id)

    answers = [answer['node'] for answer in answers]

    counts = Counter([answer['text'] for answer in answers])
    correct_answers = [answer.get('is_correct', False) for answer in answers]
    correct_answers_count = len(list(filter(bool, correct_answers)))

    return {'answers': counts, 'all_answers_count': len(answers), 'correct_answers_count': correct_answers_count}


def do_cypher_get_form_by_code(tx, code: str):
    """Вспомогательная функция для запуска Cypher-запроса на чтение"""
    return list(tx.run(f'match (node:QuestionForm) where node.code="{code}" return node;'))


def get_form_by_code(code: str):
    """Получает из Neo4j вершину с указанным классом и id"""
    driver = get_driver()

    with driver.session() as session:
        result = session.read_transaction(do_cypher_get_form_by_code, code=code)
        return result[0] if result else result
