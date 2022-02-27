from pathlib import Path  # hope to move in dedicated module in the future
import logging
from jinja2 import Template

PLACEHOLDERS = ['db_type', 'db_user', 'db_user_pass', 'db_host', 'db_port', 'db_instance']


def get_project_root() -> Path:
    """
    Method that can be used to retrieve the project root path.
    """
    return Path(__file__).parent.parent.parent.parent


class ConnectionConfig:
    def __init__(self, db_type='mysql+mysqlconnector', db_user='user', db_user_pass='pass', db_host='db',
                 db_port=3306, db_instance='generic_db_name'):
        self.db_type = db_type
        self.db_user = db_user
        self.db_user_pass = db_user_pass
        self.db_host = db_host
        self.db_port = db_port
        self.db_instance = db_instance


def generate_connection_from_template(cfg: ConnectionConfig) -> None:
    """
    Method that generates a database connection from a given configuration.

    :param cfg: A (data)class that stores the parameters of a DB connection.
    """
    with open(f'{get_project_root()}/templates/db_conn.jinja2', 'r') as f:
        db_conn_template = Template(f.read())
        db_conn_code = db_conn_template.render(cfg=cfg)
        with open(f'{get_project_root()}/generated/db.py', 'w') as gen_f:
            gen_f.write(db_conn_code)
            logging.info("Successfully generated database connection code.")


def generate_connection():
    """
    Orchestrator method that triggers the generation of the database connection Python code file.
    """
    generate_connection_from_template(ConnectionConfig())


if __name__ == "__main__":
    generate_connection()
