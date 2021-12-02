import json
from pathlib import Path


def get_project_root() -> Path:
    return Path(__file__).parent.parent.parent

datatype_converter = {
    'string': 'varchar',
    'integer': 'int(11)',
    'decimal': 'double(5, 2)',
    'boolean': 'boolean'
}


def generate_db_create_code(resources: str, path: str = f'{get_project_root()}/generated/'):
    script_string = create_database_and_use_it()
    resources_dict = json.loads(resources)

    for resource in resources_dict:
        script_string += f'CREATE TABLE `{resource["table_name"]}` (\n'
        script_string += generate_table_fields(resource["fields"])
        script_string += generate_primary_key(resource["primary_key"])
        script_string += generate_unique_keys(resource["uniques"])
        script_string += ')\n'

    script_string = script_string.replace(',\n)', '\n)')

    with open(f'{path}/create_db_and_tables.sql', 'w', encoding='utf-8') as f:
        f.write(script_string)


def generate_table_fields(fields: dict) -> str:
    script_string = ''

    for field in fields:
        script_string += f'\t`{field["name"]}` {get_sql_datatype_from_field(field)} ' \
                         f'{get_sql_nullability(field["nullable"])}, \n'

    return script_string


def generate_primary_key(pk: dict) -> str:
    return f'\tPRIMARY KEY (`{pk}`), \n'


def generate_unique_keys(unique_keys: dict) -> str:
    script_string = ''

    for unique_key in unique_keys:
        script_string = f'\tUNIQUE KEY `{unique_key["name"]}` ('
        unique_fields = unique_key["unique_fields"]
        unique_fields_tokens = [f'`{token}`' for token in unique_fields]
        script_string += ', '.join(unique_fields_tokens)

    script_string += '),\n'

    return script_string


def create_database_and_use_it(database_name: str = 'generated_db'):
    return f'CREATE DATABASE {database_name};' \
           f'\n' \
           f'USE {database_name};' \
           f'\n'


def get_sql_datatype_from_field(field: dict):
    field_type = field["type"]
    datatype = datatype_converter[field_type]

    if field_type == 'string':
        datatype += f'({field["length"]})'

    return datatype


def get_sql_nullability(is_nullable: bool):
    return 'NOT NULL' if not is_nullable else ''


# testing purpose
generate_db_create_code(json.dumps([
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
                    "title",
                    "year_of_publishing"
                ]
            }
        ]
    }
]))
