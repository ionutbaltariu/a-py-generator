from jinja2 import Template
from pathlib import Path
from utils import get_project_root
from typing import List
import logging
import os

GENERATED_PATH = f"{get_project_root()}/generated"


def create_routers_folder(path: str):
    os.mkdir(os.path.join(path, "routers"), 0o777)
    Path(f"{GENERATED_PATH}/routers/__init__.py").touch()


def create_utils_file(resources: List[dict]):
    with open(f'{get_project_root()}/templates/utils.jinja2', 'r') as f:
        utils_template = Template(f.read(), trim_blocks=True, lstrip_blocks=True)
        with open(f'{get_project_root()}/generated/utils.py', 'w', encoding='utf-8') as gen_f:
            gen_f.write(utils_template.render(resources=resources))
            logging.info(f"Successfully generated utils file.")


def create_routers(resources: List[dict]):
    with open(f'{get_project_root()}/templates/router.jinja2', 'r') as f:
        router_template = Template(f.read(), trim_blocks=True, lstrip_blocks=True)
        # TODO: add 'generated' directory in path after figuring out how to import modules from '..'
        for resource in resources:
            with open(f'{get_project_root()}/generated/{resource["name"].lower()}_router.py', 'w',
                      encoding='utf-8') as gen_f:
                gen_f.write(router_template.render(entity=resource))
                logging.info(f"Successfully generated router for the '{resource['name'].lower()}' entity.")


def create_main_app(resources: List[dict]):
    with open(f'{get_project_root()}/templates/main_fastapi.jinja2', 'r') as f:
        app_template = Template(f.read(), trim_blocks=True, lstrip_blocks=True)
        with open(f'{get_project_root()}/generated/main.py', 'w', encoding='utf-8') as gen_f:
            gen_f.write(app_template.render(resources=resources))
            logging.info(f"Successfully generated main app.")


def generate_fastapi_code(resources):
    # create_routers_folder(GENERATED_PATH)
    create_utils_file(resources)
    # TODO: add errors for each entity (replace in jinja template as well)
    create_routers(resources)
    create_main_app(resources)