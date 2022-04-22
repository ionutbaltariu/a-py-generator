import logging
from utils import get_project_root
from jinja2 import Template
from typing import List


def generate_model_code(resources_dict: List[dict]) -> None:
    """
    Method that triggers the 'model.py' code generation - file contains code that's use to perform database operations
    :param resources_dict: dictionary that contains the input resources
    """
    with open(f'{get_project_root()}/templates/model.jinja2', 'r') as f:
        model_template = Template(f.read(), trim_blocks=True, lstrip_blocks=True)
        model_code = model_template.render(entities=resources_dict)

        with open(f'{get_project_root()}/generated/model.py', 'w', encoding='utf-8') as gen_f:
            gen_f.write(model_code)
            logging.info(f"Successfully generated model code.")