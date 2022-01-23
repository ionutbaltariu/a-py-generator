import json
import logging
from pathlib import Path  # hope to move in dedicated module in the future


def get_project_root() -> Path:
    return Path(__file__).parent.parent.parent.parent  # ./../../


datatype_converter = {
    'string': 'sqlalchemy.String',
    'integer': 'sqlalchemy.Integer',
    'decimal': 'sqlalchemy.Float',
    'boolean': 'sqlalchemy.Boolean'
}


def generate_sqlalchemy_classes(resources: str) -> None:
    """
    Orchestrator method that triggers the generation of the SQLAlchemy classes based on the input resources.

    :param resources: Serialized List of resources
    """
    resources_dict = json.loads(resources)
    for resource in resources_dict:
        sqlalchemy_code = 'import sqlalchemy\n'
        sqlalchemy_code += 'from db import Base\n\n\n'
        sqlalchemy_code += f'class {resource["name"]}(Base):\n'
        sqlalchemy_code += f'\t__tablename__ = \'{resource["table_name"]}\'\n'
        sqlalchemy_code += generate_sqlalechemy_class_fields(resource)

        with open(f'{get_project_root()}/generated/{resource["name"]}.py', 'w', encoding='utf-8') as f:
            f.write(sqlalchemy_code)
            logging.info(f"Successfully generated SQLAlchemy Model class `{resource['name']}`.")


def generate_sqlalechemy_class_fields(resource: dict) -> str:
    """
    Method that generates the fields of a SQLAlchemy Model class.

    :param resource: Resource in the dictionary format
    :return: a string(str) representing the equivalent Python code
    """
    primary_key_field = resource["primary_key"]
    sqlalchemy_code = ''
    # look for another way, this approach is checking at every field
    for field in resource["fields"]:
        is_primary_key = (primary_key_field == field["name"])
        sqlalchemy_code += generate_class_field_from_resource(field, is_primary_key)

    sqlalchemy_code += '\n\n'

    return sqlalchemy_code


def generate_class_field_from_resource(field: dict, is_primary_key: bool) -> str:
    """
    Method that generates a field based on a dictionary.

    :param field: The field of a resource
    :param is_primary_key: Boolean that indicates if the field is the primary key or not
    :return: a string(str) representing the equivalent Python code line
    """
    tokens = []

    if field["type"] == "string":
        tokens.append(f'{datatype_converter["string"]}({field["length"]})')
    else:
        tokens.append(datatype_converter[field["type"]])

    tokens.append('nullable=True' if field["nullable"] is True else 'nullable=False')

    if is_primary_key:
        tokens.append('primary_key=True')

    deconstructed_tokens = ', '.join(tokens)

    generated_field = f'\t{field["name"]} = sqlalchemy.Column({deconstructed_tokens})\n'

    return generated_field
