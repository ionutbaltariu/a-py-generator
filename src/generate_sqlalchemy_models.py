import logging
from utils import get_project_root
from jinja2 import Template
from dataclasses import dataclass
from typing import List, Optional


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


datatype_converter = {
    'string': 'sqlalchemy.String',
    'integer': 'sqlalchemy.Integer',
    'decimal': 'sqlalchemy.Float',
    'boolean': 'sqlalchemy.Boolean'
}


def generate_sqlalchemy_classes(resources: List[dict]) -> None:
    with open(f'{get_project_root()}/templates/sqlalchemy_model.jinja2', 'r') as f:
        sqlalchemy_template = Template(f.read(), trim_blocks=True, lstrip_blocks=True)
        for resource in resources:
            fields = []

            for field in resource["fields"]:
                field_attributes = get_attributes_from_field(field, (field["name"] == resource["primary_key"]))

                if resource["foreign_keys"] is not None:
                    for foreign_key in resource["foreign_keys"]:
                        if field["name"] == foreign_key["field"]:
                            # nasty workaround
                            # insert ForeignKey attribute at position 1
                            field_attributes.insert(1, f'sqlalchemy.ForeignKey("{foreign_key["references"]}.'
                                                       f'{foreign_key["reference_field"]}")')
                            break

                fields.append(Field(field["name"], field_attributes))

            uniques = resource["uniques"] if "uniques" in resource else None

            sqlalchemy_code = sqlalchemy_template.render(resource=Resource(resource["name"],
                                                                           resource["table_name"],
                                                                           fields,
                                                                           uniques))

            with open(f'{get_project_root()}/generated/{resource["name"]}.py', 'w', encoding='utf-8') as gen_f:
                gen_f.write(sqlalchemy_code)
                logging.info(f"Successfully generated SQLAlchemy Model class `{resource['name']}`.")


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
