import json

datatype_converter = {
    'string': 'varchar',
    'integer': 'int(11)',
    'decimal': 'double(5, 2)',
    'boolean': 'boolean'
}


def generate_db_create_code(path: str, resources: str):
    with open(f'{path}/create_db_and_tables.sql', 'w', encoding='utf-8') as f:
        script_string = ''
        script_string += create_database_and_use_it()

        resources_dict = json.loads(resources)
        for resource in resources_dict:
            script_string += f'CREATE TABLE `{resource["table_name"]}` (\n'
            fields = resource['fields']
            for field in fields:
                script_string += f'\t`{field["name"]}` {get_sql_datatype_from_field(field)} ' \
                                 f'{get_sql_nullability(field["nullable"])}, \n'

            script_string += f'\tPRIMARY KEY (`{resource["primary_key"]}`), \n'

            for unique_key in resource["uniques"]:
                script_string += f'\tUNIQUE KEY `{unique_key["name"]}` ('
                unique_fields = unique_key["unique_fields"]
                unique_fields_len = len(unique_fields) - 1
                for index, field in enumerate(unique_fields):
                    script_string += f'`{field}`'
                    if index != unique_fields_len:
                        script_string += ', '
                script_string += '),\n'

            script_string += ')\n'

        f.write(script_string)


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
generate_db_create_code('.', json.dumps([
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
