from dataclasses import dataclass
from typing import List
from Generator import ResourceBasedGenerator


# Adapter classes so that the dynamic parts of the templates can be replaced easier (with little processing)

@dataclass
class Field:
    name: str
    attributes: List[str]


@dataclass
class Unique:
    name: str
    unique_fields: List[str]


@dataclass
class Relationship:
    type: str
    table: str
    reference_field: str
    role: str
    resource: str


@dataclass
class Resource:
    name: str
    table_name: str
    fields: List[Field]
    uniques: List[Unique]
    relationships: List[Relationship]


datatype_converter = {
    'string': 'sqlalchemy.String',
    'integer': 'sqlalchemy.Integer',
    'decimal': 'sqlalchemy.Float',
    'boolean': 'sqlalchemy.Boolean',
    'date': 'sqlalchemy.Date'
}


class ConnectionConfig:
    def __init__(self, db_type='mysql+mysqlconnector', db_user='root', db_user_pass='password', db_host='localhost',
                 db_port=3306, db_instance='generated_db'):
        self.db_type = db_type
        self.db_user = db_user
        self.db_user_pass = db_user_pass
        self.db_host = db_host
        self.db_port = db_port
        self.db_instance = db_instance


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


class SQLAlchemyGenerator(ResourceBasedGenerator):
    def __init__(self, resources: List[dict], generation_uid):
        super().__init__(resources, generation_uid)
        self.db_connection_config = ConnectionConfig()
        self.db_conn_template = self.read_template_from_file('db_conn.jinja2')
        self.sqlalchemy_template = self.read_template_from_file('sqlalchemy_model.jinja2')
        self.model_template = self.read_template_from_file('model_sql.jinja2')

    def generate_connection_from_template(self) -> None:
        """
        Method that generates a database connection from a given configuration.
        """
        db_conn_code = self.db_conn_template.render(cfg=self.db_connection_config)
        self.write_to_src('db.py', db_conn_code)

    def generate_sqlalchemy_classes(self) -> None:
        # TODO: Refactor down to small, understandable pieces
        for resource in self.resources:
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

            # getting the name of the referenced resource by the table
            # can be refactored by handling relationships with referenced to other resources instead of tables
            relationships = resource.get("relationships")

            if relationships:
                for rel in relationships:
                    rel["resource"] = [x for x in self.resources
                                       if x.get("table_name") == rel.get("table")][0].get("name")

            sqlalchemy_code = self.sqlalchemy_template.render(resource=Resource(resource["name"],
                                                                                resource["table_name"],
                                                                                fields,
                                                                                uniques,
                                                                                relationships))
            self.write_to_src(f'{resource["name"]}.py', sqlalchemy_code)

    def generate_model_code(self) -> None:
        """
        Method that triggers the 'model.py' code generation - file contains code that's used to
        perform database operations
        """
        model_code = self.model_template.render(entities=self.resources)
        self.write_to_src('model.py', model_code)

    def generate(self):
        self.generate_connection_from_template()
        self.generate_sqlalchemy_classes()
        self.generate_model_code()
