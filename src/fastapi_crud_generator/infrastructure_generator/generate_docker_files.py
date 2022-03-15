import logging
from jinja2 import Template
from pathlib import Path


def get_project_root() -> Path:
    return Path(__file__).parent.parent.parent.parent  # ./../../


def generate_docker_compose():
    with open(f'{get_project_root()}/templates/docker_compose.jinja2', 'r') as f:
        docker_compose_template = Template(f.read(), trim_blocks=True, lstrip_blocks=True)
        with open(f'{get_project_root()}/generated/docker-compose.yml', 'w', encoding='utf-8') as gen_f:
            gen_f.write(docker_compose_template.render())
            logging.info(f"Successfully generated docker compose.")


generate_docker_compose()
