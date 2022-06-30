from Generator import ResourceBasedGenerator
from dataclasses import dataclass
from typing import List

datatype_converter = {
    'string': 'varchar({length})',
    'integer': 'int(11)',
    'decimal': 'double(5, 2)',
    'boolean': 'boolean',
    'date': 'date'
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


class SQLGenerator(ResourceBasedGenerator):
    def __init__(self, resources: List[dict], generation_uid):
        """
        :param resources: the list of resources defined by the user
        :param generation_uid: the identifier of the generation, used to group the source code in a directory
        """
        super().__init__(resources, generation_uid)
        self.sql_template = self.read_template_from_file('sql.jinja2')

    def generate(self) -> None:
        """
        Method that generates SQL code based on a given List of resources.
        """
        tables_to_be_created = []

        for resource in self.resources:
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

        sql_code = self.sql_template.render(tables=tables_to_be_created)
        self.write_to_gen_path('create_db_and_tables.sql', sql_code)
