import json
import logging
from utils import get_project_root
from dataclasses import dataclass
from typing import List
from jinja2 import Template

datatype_converter = {
    'string': 'varchar({length})',
    'integer': 'int(11)',
    'decimal': 'double(5, 2)',
    'boolean': 'boolean'
}


@dataclass
class Field:
    name: str
    type: str
    nullability: str

    def get_sql_datatype_from_field(self, field: dict):
        """
        Method that translates a resource type into an SQL type (MariaDB).

        :param field: The field of which type is to be translated
        """
        field_type = field["type"]

        if field_type == 'string':
            self.type = datatype_converter[field_type].format(length=field["length"])
        else:
            self.type = datatype_converter[field_type]

    def get_sql_nullability(self, is_nullable: bool):
        """
        Method that returns the code to specify the nullability of a table field.
        """
        self.nullability = 'NOT NULL' if not is_nullable else ''

    def __init__(self, field: dict):
        self.name = field["name"]
        self.get_sql_datatype_from_field(field)
        self.get_sql_nullability(field["nullable"])


@dataclass
class Unique:
    name: str
    unique_fields: List[str]


@dataclass
class ForeignKey:
    field: str
    references: str
    reference_field: str


@dataclass
class Table:
    name: str
    fields: List[Field]
    uniques: List[Unique]
    primary_key: str
    foreign_keys: List[ForeignKey]


def generate_db_create_code(resources: List[dict], path: str = f'{get_project_root()}/generated/') -> None:
    """
    Method that generates SQL code based on a given List of resources.

    :param resources: a List of resources that will be translated into SQL tables.
    :param path: [out] The path in which the code will be generated.
    """
    logging.info(f"Entered {generate_db_create_code.__name__}")
    tables_to_be_created = []

    for resource in resources:
        temp_fields = []
        temp_uniques = []
        temp_fks = []

        for field in resource['fields']:
            temp_fields.append(Field(field))
        if 'uniques' in resource and resource['uniques'] is not None:
            temp_uniques = [Unique(**unique) for unique in resource['uniques']]

        if 'foreign_keys' in resource and resource['foreign_keys'] is not None:
            temp_fks = [ForeignKey(**foreign_key) for foreign_key in resource['foreign_keys']]

        tables_to_be_created.append(Table(name=resource['table_name'],
                                          fields=temp_fields,
                                          uniques=temp_uniques,
                                          foreign_keys=temp_fks,
                                          primary_key=resource['primary_key']))

    with open(f'{get_project_root()}/templates/sql.jinja2', 'r') as f:
        sql_template = Template(f.read(), trim_blocks=True)
        sql_code = sql_template.render(tables=tables_to_be_created)

        with open(f'{path}/create_db_and_tables.sql', 'w', encoding='utf-8') as gen_f:
            gen_f.write(sql_code)
            logging.info(f"Successfully created SQL script at path `{path}`.")