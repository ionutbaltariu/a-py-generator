import json
import logging
from utils import get_project_root
from dataclasses import dataclass
from typing import List
from jinja2 import Template

datatype_converter = {
    'string': 'sqlalchemy.String',
    'integer': 'sqlalchemy.Integer',
    'decimal': 'sqlalchemy.Float',
    'boolean': 'sqlalchemy.Boolean'
}

pseudocode_to_pydantic = {
    'string': 'constr(min_length=1, max_length={length})',
    'integer': 'int',
    'decimal': 'float',
    'boolean': 'bool'
}


@dataclass
class Field:
    name: str
    attributes: List[str]


@dataclass
class Unique:
    name: str
    unique_fields: List[str]


@dataclass
class Resource:
    name: str
    table_name: str
    fields: List[Field]
    uniques: List[Unique]


@dataclass
class PydanticField:
    name: str
    type: str


@dataclass
class PydanticResource:
    name: str
    primary_key: str
    fields: List[PydanticField]


def generate_infrastructure(resources: str) -> None:
    """
    Orchestrator method that triggers the generation of all code.

    :param resources: Serialized List of resources
    """
    resources_dict = json.loads(resources)

    generate_sqlalchemy_classes(resources_dict)
    generator_model_code(resources_dict)
    generate_pydantic_models(resources_dict)


def generate_pydantic_models(resources_dict: dict) -> None:
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


def generate_sqlalchemy_classes(resources_dict: dict) -> None:
    with open(f'{get_project_root()}/templates/sqlalchemy_model.jinja2', 'r') as f:
        sqlalchemy_template = Template(f.read(), trim_blocks=True, lstrip_blocks=True)

        for resource in resources_dict:
            fields = []
            for field in resource["fields"]:
                fields.append(Field(field["name"],
                                    get_attributes_from_field(field, (field["name"] == resource["primary_key"]))))

            uniques = resource["uniques"] if "uniques" in resource else None

            sqlalchemy_code = sqlalchemy_template.render(resource=Resource(resource["name"],
                                                                           resource["table_name"],
                                                                           fields,
                                                                           uniques))

            with open(f'{get_project_root()}/generated/{resource["name"]}.py', 'w', encoding='utf-8') as gen_f:
                gen_f.write(sqlalchemy_code)
                logging.info(f"Successfully generated SQLAlchemy Model class `{resource['name']}`.")


def generator_model_code(resources_dict: dict) -> None:
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


def get_attributes_from_field(field: dict, is_primary_key: bool):
    """
    Function used to get the list of attributes from a field so they can be persisted in the sqlalchemy.Column

    :param field: dictionary that holds field related properties
    :param is_primary_key: boolean that indicates whether the field is a primary key or not
    :return: a list of strings containing the raw attributes
    """
    attributes = []

    if field["type"] == "string":
        attributes.append(f'{datatype_converter["string"]}({field["length"]})')
    else:
        attributes.append(datatype_converter[field["type"]])

    attributes.append("nullable=True" if field["nullable"] is True else "nullable=False")

    if is_primary_key:
        attributes.append("primary_key=True")

    return attributes
