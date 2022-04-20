from pydantic import BaseSettings


ENV_FILE = '.env'


class AppConfig(BaseSettings):
    IS_HEROKU: bool = False


class Neo4jConfig(BaseSettings):
    class Config:
        env_prefix = 'neo4j_'

    uri: str = ''
    username: str = 'neo4j'
    password: str = ''

neo4j_config = Neo4jConfig(ENV_FILE)
app_config = AppConfig(ENV_FILE)
