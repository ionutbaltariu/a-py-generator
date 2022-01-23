import json
import logging
from pathlib import Path


def get_project_root() -> Path:
    return Path(__file__).parent.parent.parent.parent


datatype_converter = {
    'string': 'varchar({length})',
    'integer': 'int(11)',
    'decimal': 'double(5, 2)',
    'boolean': 'boolean'
}


def generate_db_create_code(resources: str, path: str = f'{get_project_root()}/generated/') -> None:
    """
    Method that generates SQL code based on a given List of resources.

    :param resources: a List of resources that will be translated into SQL tables.
    :param path: [out] The path in which the code will be generated.
    """
    logging.info(f"Entered {generate_db_create_code.__name__}")
    script_string = create_database_and_use_it()
    resources_dict = json.loads(resources)

    for resource in resources_dict:
        script_string += f'CREATE TABLE `{resource["table_name"]}` (\n'
        script_string += generate_table_fields(resource["fields"])
        script_string += generate_primary_key(resource["primary_key"])
        if resource["uniques"] is not None:
            script_string += generate_unique_keys(resource["uniques"])
        script_string += ');\n\n'

    script_string = script_string.replace(',\n)', '\n)')

    with open(f'{path}/create_db_and_tables.sql', 'w', encoding='utf-8') as f:
        f.write(script_string)
        logging.info(f"Successfully created SQL script at path `{path}`.")


def generate_table_fields(fields: dict) -> str:
    """
    Method that generates the fields of an SQL table.

    :param fields: a Dictionary representing the fields of a resource
    :return: The string equivalent of the table's fields.
    """
    script_string = ''

    for field in fields:
        script_string += f'\t`{field["name"]}` {get_sql_datatype_from_field(field)} ' \
                         f'{get_sql_nullability(field["nullable"])}, \n'

    return script_string


def generate_primary_key(primary_key_field: str) -> str:
    """
    Method that generates a primary key constraint with the input field.
    """
    return f'\tPRIMARY KEY (`{primary_key_field}`),\n'


def generate_unique_keys(unique_keys: dict) -> str:
    script_string = ''

    for unique_key in unique_keys:
        script_string = f'\tUNIQUE KEY `{unique_key["name"]}` ('
        unique_fields = unique_key["unique_fields"]
        unique_fields_tokens = [f'`{token}`' for token in unique_fields]
        script_string += ', '.join(unique_fields_tokens)

    script_string += '),\n'

    return script_string


def create_database_and_use_it(database_name: str = 'generated_db') -> str:
    """
    Method that generates the SQL code that creates a database and uses it.
    """
    return f'CREATE DATABASE {database_name};' \
           f'\n' \
           f'USE {database_name};' \
           f'\n'


def get_sql_datatype_from_field(field: dict) -> str:
    """
    Method that translates a resource type into an SQL type (MariaDB).

    :param field: The field of which type is to be translated
    :return: The equivalent MariaDB type for the field.
    """
    field_type = field["type"]

    if field_type == 'string':
        datatype = datatype_converter[field_type].format(length=field["length"])
    else:
        datatype = datatype_converter[field_type]

    return datatype


def get_sql_nullability(is_nullable: bool):
    """
    Method that returns the code to specify the nullability of a table field.
    """
    return 'NOT NULL' if not is_nullable else ''
