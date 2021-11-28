import json

datatype_converter = {
    'string': 'sqlalchemy.String',
    'integer': 'sqlalchemy.Integer',
    'decimal': 'sqlalchemy.Float',
    'boolean': 'sqlalchemy.Boolean'
}


# class Book(Base):
#    __tablename__ = 'books'


def generate_sqlalchemy_classes(resources):
    sqlalchemy_code = 'import sqlalchemy\n\n'
    resources_dict = json.loads(resources)
    for resource in resources_dict:
        sqlalchemy_code += f'class {resource["name"]}(sqlalchemy.Base):\n'
        sqlalchemy_code += f'\t__tablename = \'{resource["table_name"]}\'\n'
        sqlalchemy_code += generate_sqlalechemy_class_fields(resource)

    with open(f'./smth.py', 'w', encoding='utf-8') as f:
        f.write(sqlalchemy_code)


def generate_sqlalechemy_class_fields(resource):
    sqlalchemy_code = ''
    for field in resource["fields"]:
        sqlalchemy_code += generate_class_field_from_resource(field)

    sqlalchemy_code += '\n\n'

    return sqlalchemy_code


def generate_class_field_from_resource(field):
    tokens = []

    if field["type"] == "string":
        tokens.append(f'{datatype_converter["string"]}({field["length"]})')
    else:
        tokens.append(datatype_converter[field["type"]])

    tokens.append('nullable=True' if field["nullable"] is True else 'nullable=False')

    deconstructed_tokens = ', '.join(tokens)

    generated_field = f'\t{field["name"]} = sqlalchemy.Column({deconstructed_tokens})\n'

    return generated_field



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
