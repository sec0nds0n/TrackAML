# app/extensions.py

from flask_session import Session
from neo4j import GraphDatabase

flask_session_ext = Session()

class Neo4jDriver:
    def __init__(self):
        self.driver = None

    def init_app(self, app):
        uri = app.config['NEO4J_URI']
        user = app.config['NEO4J_USER']
        pwd = app.config['NEO4J_PASSWORD']
        self.driver = GraphDatabase.driver(uri, auth=(user, pwd))

    def get_driver(self):
        return self.driver

neo4j_driver = Neo4jDriver()