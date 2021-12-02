from pathlib import Path  # hope to move in dedicated module in the future

PLACEHOLDERS = ['db_type', 'db_user', 'db_user_pass', 'db_host', 'db_port', 'db_instance']


def get_project_root() -> Path:
    return Path(__file__).parent.parent.parent


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
    with open(f'{get_project_root()}/templates/db_conn.txt', 'r') as f:
        generated_code = replace_all_placeholders(f.read(), cfg)
        with open(f'{get_project_root()}/generated/db.py', 'w') as gen_f:
            gen_f.write(generated_code)


def replace_all_placeholders(generated_code: str, cfg: ConnectionConfig) -> str:
    for placeholder in PLACEHOLDERS:
        generated_code = generated_code.replace(f'{{{placeholder}}}', f'\'{str(getattr(cfg, placeholder))}\'')

    return generated_code


generate_connection_from_template(ConnectionConfig())
