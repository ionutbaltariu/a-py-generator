import json
import logging
from utils import get_project_root
from dataclasses import dataclass
from typing import List
from jinja2 import Template

pseudocode_to_pydantic = {
    'string': 'constr(min_length=1, max_length={length})',
    'integer': 'int',
    'decimal': 'float',
    'boolean': 'bool'
}


@dataclass
class PydanticField:
    name: str
    type: str


@dataclass
class PydanticResource:
    name: str
    primary_key: str
    fields: List[PydanticField]


def generate_pydantic_models(resources_dict: List[dict]) -> None:
    resources = []
    for resource in resources_dict:
        fields = []
        for field in resource["fields"]:
            if field["type"] == "string":
                field_type = pseudocode_to_pydantic["string"].format(length=field["length"])
            else:
                field_type = pseudocode_to_pydantic[field["type"]]

            fields.append(PydanticField(field["name"], field_type))
        resources.append(PydanticResource(resource["name"], resource["primary_key"], fields))

    # TODO refactor; make a generic generation method - code is duplicated (generator_model_code)
    with open(f'{get_project_root()}/templates/pydantic.jinja2', 'r') as f:
        pydantic_template = Template(f.read(), trim_blocks=True, lstrip_blocks=True)
        pydantic_code = pydantic_template.render(resources=resources)
        with open(f'{get_project_root()}/generated/view.py', 'w', encoding='utf-8') as gen_f:
            gen_f.write(pydantic_code)
            logging.info(f"Successfully generated pydantic models.")



