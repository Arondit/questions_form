from app.neo4j_tools.neo4j_connection import get_driver


def do_cypher_edit(tx, class_name, node_id, **attributes):
    """Вспомогательная функция для запуска Cypher-запроса на редактирование"""
    attributes_string = ', '.join(f'node.{key}= "{value}"' for key, value in attributes.items() if value)

    tx.run(f'match (node:{class_name}) where id(node)={node_id} set {attributes_string} return node')


def edit_node(class_name, node_id, **attributes):
    """Редактирует в Neo4j вершину с указанным классом и id, проставляя полученные атрибуты"""
    driver = get_driver()

    with driver.session() as session:
        session.write_transaction(do_cypher_edit, class_name=class_name, node_id=node_id, **attributes)
