import json
import logging
from pathlib import Path  # hope to move in dedicated module in the future
from dataclasses import dataclass
from typing import List
from jinja2 import Template


def get_project_root() -> Path:
    return Path(__file__).parent.parent.parent.parent  # ./../../


datatype_converter = {
    'string': 'sqlalchemy.String',
    'integer': 'sqlalchemy.Integer',
    'decimal': 'sqlalchemy.Float',
    'boolean': 'sqlalchemy.Boolean'
}


@dataclass
class Field:
    name: str
    attributes: List[str]


@dataclass
class Resource:
    name: str
    table_name: str
    fields: List[Field]


def generate_sqlalchemy_classes(resources: str) -> None:
    """
    Orchestrator method that triggers the generation of the SQLAlchemy classes based on the input resources.

    :param resources: Serialized List of resources
    """
    resources_dict = json.loads(resources)

    with open(f'{get_project_root()}/templates/sqlalchemy_model.jinja2', 'r') as f:
        sqlalchemy_template = Template(f.read(), trim_blocks=True, lstrip_blocks=True)

        for resource in resources_dict:
            fields = []
            for field in resource["fields"]:
                fields.append(Field(field["name"], get_attributes_from_field(field,
                                                                             (field["name"] == resource["primary_key"])
                                                                             )
                                    ))

            sqlalchemy_code = sqlalchemy_template.render(resource=Resource(resource["name"],
                                                                           resource["table_name"],
                                                                           fields))

            with open(f'{get_project_root()}/generated/{resource["name"]}.py', 'w', encoding='utf-8') as gen_f:
                gen_f.write(sqlalchemy_code)
                logging.info(f"Successfully generated SQLAlchemy Model class `{resource['name']}`.")

    # this currently generates "model.py" code for all resources
    # TODO: think more about code structure
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


generate_sqlalchemy_classes(json.dumps([
    {
        "name": "Book",
        "table_name": "Books",
        "fields": [
            {
                "name": "isbn",
                "type": "string",
                "length": 100,
                "nullable": False
            },
            {
                "name": "title",
                "type": "string",
                "length": 100,
                "nullable": False
            },
            {
                "name": "year_of_publishing",
                "type": "integer",
                "nullable": False
            }
        ],
        "primary_key": "isbn",
        "uniques": [
            {
                "name": "books_un_1",
                "unique_fields": [
                    "title"
                ]
            }
        ]
    }
]))
