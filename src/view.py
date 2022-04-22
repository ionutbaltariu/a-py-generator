import networkx.exception
from pydantic import BaseModel, constr, validator, Extra
from typing import List, Optional, Literal
from networkx import DiGraph, find_cycle
from keyword import iskeyword
from config import MAX_RESOURCES_ALLOWED

def generic_alphanumeric_validator(element: str, element_name: str) -> None:
    if not element.replace('_', '').isalnum():
        raise ValueError(f"A(n) {element_name} can only contain alphabetic characters and '_'.")


def generic_keyword_verifier(element: str, element_name: str) -> None:
    if iskeyword(element):
        raise ValueError(f"A(n) {element_name}  cannot be equivalent to a Python keyword.")


def string_must_not_start_with_number_verifier(element: str, element_name: str) -> None:
    if element[:1].isdigit():
        raise ValueError(f"A(n) {element_name}'s name cannot begin with a number.")


def generic_alphanumeric_and_keyword_validator(element: str, element_name: str) -> None:
    generic_keyword_verifier(element, element_name)
    generic_alphanumeric_validator(element, element_name)
    string_must_not_start_with_number_verifier(element, element_name)


class Field(BaseModel, extra=Extra.forbid):
    name: constr(min_length=1, max_length=64)
    type: Literal["integer", "string", "decimal", "boolean"]
    length: Optional[int]
    nullable: bool

    @validator('length')
    def length_must_me_reasonable(cls, v, values):
        if v > 255:
            raise ValueError(f"Length of a string field cannot be greater than 255 ('{values['name']}')!")
        elif v < 1:
            raise ValueError("Length of a string field cannot be lesser than 1 / negative ('{values['name']}')!")

        return v

    @validator('name')
    def name_alpha_and_not_keyword(cls, v):
        generic_alphanumeric_and_keyword_validator(v, 'field name')
        return v


class Unique(BaseModel, extra=Extra.forbid):
    name: constr(min_length=1, max_length=64)
    unique_fields: List[constr(min_length=1, max_length=64)]


class Relationship(BaseModel, extra=Extra.forbid):
    type: Literal["ONE-TO-ONE", "ONE-TO-MANY", "MANY-TO-MANY"]
    table: constr(min_length=1, max_length=64)
    reference_field: Optional[constr(min_length=1, max_length=64)]


class ForeignKey(BaseModel, extra=Extra.forbid):
    field: constr(min_length=1, max_length=64)
    references: constr(min_length=1, max_length=64)
    reference_field: constr(min_length=1, max_length=64)


class Resource(BaseModel, extra=Extra.forbid):
    name: constr(min_length=1, max_length=64)
    table_name: constr(min_length=1, max_length=64)
    fields: List[Field]
    primary_key: constr(min_length=1, max_length=64)
    uniques: Optional[List[Unique]]
    relationships: Optional[List[Relationship]]
    foreign_keys: Optional[List[ForeignKey]]

    @validator('fields')
    def resource_must_not_have_duplicate_fields(cls, v):
        field_names = [field.name.lower() for field in v]

        if len(set(field_names)) != len(field_names):
            raise ValueError(f"Please make sure that there are no duplicate field names in the input!")

        return v

    @validator('name')
    def resource_name_must_be_pure_string(cls, v):
        generic_alphanumeric_and_keyword_validator(v, 'resource name')
        return v

    @validator('table_name')
    def table_name_must_be_pure_string(cls, v):
        generic_alphanumeric_and_keyword_validator(v, 'table name')
        return v

    @validator('primary_key')
    def primary_key_must_be_in_fields(cls, v, values):
        if "fields" not in values:
            return v

        fieldnames = [field.name for field in values["fields"]]

        if v not in fieldnames:
            raise ValueError(f"Primary key `{v}` should be one of the input fields.")
        return v

    @validator('uniques')
    def uniques_names_must_be_alphanumeric(cls, v):
        for unique in v:
            generic_alphanumeric_and_keyword_validator(unique.name, 'unique name')

        return v

    @validator('uniques')
    def unique_keys_must_be_in_fields(cls, v, values):
        if "fields" not in values:
            return v

        fieldnames = [field.name.lower() for field in values["fields"]]

        for unique_constr in v:
            generic_alphanumeric_validator(unique_constr.name, 'unique constraint name')
            for unique_field in unique_constr.unique_fields:
                if unique_field.lower() not in fieldnames:
                    raise ValueError(f"Unique `{unique_constr.name}` contains a field that was not declared:"
                                     f" `{unique_field}`")
        return v

    @validator('uniques')
    def unique_container_must_not_have_duplicates(cls, v):
        unique_names = [unique.name.lower() for unique in v]

        if len(set(unique_names)) != len(unique_names):
            raise ValueError(f"Please make sure that there are no duplicate unique names in the input!")

        return v

    @validator('uniques')
    def check_for_duplicate_unique_pairs(cls, v):
        list_of_unique_pairs = [unique.unique_fields for unique in v]

        for i in range(len(list_of_unique_pairs)):
            for j in range(len(list_of_unique_pairs)):
                if i != j and [x.lower() for x in list_of_unique_pairs[i]] == [x.lower() for x in
                                                                               list_of_unique_pairs[j]]:
                    raise ValueError(f"Please make sure that there are no duplicate unique pairs in the input.")

        return v


class Input(BaseModel, extra=Extra.forbid):
    resources: List[Resource]

    @validator('resources')
    def resource_list_cannot_be_empty(cls, v):
        if(len(v)) == 0:
            raise ValueError("Input resource list cannot be empty!")

        return v

    @validator('resources')
    def resource_list_cannot_be_huge(cls, v):
        if len(v) > MAX_RESOURCES_ALLOWED:
            raise ValueError(f"Input resource list cannot contain more than {MAX_RESOURCES_ALLOWED} elements.")

        return v

    @validator('resources')
    def check_for_duplicate_resource_names(cls, v):
        resource_names = [resource.name.lower() for resource in v]

        if len(set(resource_names)) != len(resource_names):
            raise ValueError(f"Please make sure that there are no duplicate resource names in the input.")

        return v

    @validator('resources')
    def check_for_duplicate_table_names(cls, v):
        table_names = [resource.table_name.lower() for resource in v]

        if len(set(table_names)) != len(table_names):
            raise ValueError(f"Please make sure that there are no duplicate table names in the input.")

        return v

    @validator('resources')
    def validate_and_create_relationships(cls, v):
        # TODO: refactor because the function is too long
        tables_names = [x.table_name for x in v]
        relationships = DiGraph()

        for table_name in tables_names:
            relationships.add_node(table_name)

        for resource in v:
            # guard for the resources that do not have relationship
            if not resource.relationships:
                continue

            for relation in resource.relationships:
                if relation.table == resource.table_name:
                    raise ValueError("A table cannot have a relationship with itself.")
                elif relation.table not in tables_names:
                    raise ValueError(f"Table '{resource.table_name}' has a relationship with a table that does not "
                                     f"exist in the given list of resources.")
                relationships.add_edge(resource.table_name,
                                       relation.table,
                                       rel_type=relation.type,
                                       referenced_field=relation.reference_field)

        try:
            cycle = find_cycle(relationships)
            cycle = ' -> '.join([f"({x[0]}, {x[1]})" for x in cycle])
            raise ValueError(f"There are circular relationships in the given list of resources. Please revise: {cycle}")
        except networkx.exception.NetworkXNoCycle:
            # there were no cycles and the list of resources can be updated to contain the new foreign keys and eventual
            # link tables (many-to-many)
            # TODO: idea: use factory pattern to handle actions based on relationship type
            for table1, table2, data in relationships.edges(data=True):
                rel_type = data["rel_type"]
                referenced_field = data["referenced_field"]

                if referenced_field is not None and rel_type == "MANY-TO-MANY":
                    raise ValueError(f"There should not be a referenced field"
                                     f" when the relationship type is 'MANY-TO-MANY'")
                if referenced_field is None and rel_type != "MANY-TO-MANY":
                    raise ValueError(f"Please introduce a referenced field in the child table.")

                table1 = list(filter(lambda x: x.table_name == table1, v))[0]
                table2 = list(filter(lambda x: x.table_name == table2, v))[0]
                table1_field = list(filter(lambda x: x.name == referenced_field, table1.fields))

                if len(table1_field) == 0:
                    raise ValueError(f"The referenced field should exist in '{table1.table_name}'!")

                if rel_type == "MANY-TO-MANY":
                    fields = [Field(name=f"id", type="integer", nullable=False),
                              Field(name=f"{table1.primary_key}", type="integer", nullable=False),
                              Field(name=f"{table2.primary_key}", type="integer", nullable=False)]
                    table_name = f"{table1.table_name}_{table2.table_name}"
                    # TODO: when support for composite primary keys will be added, also change here
                    link_table = Resource(name=table_name, table_name=table_name, fields=fields, primary_key="id")
                    v.append(link_table)
                    create_fk_many_to_many(link_table, table1, fields[1].name)
                    create_fk_many_to_many(link_table, table2, fields[2].name)
                elif rel_type == "ONE-TO-ONE":
                    create_fk(master=table2, slave=table1, reference_field=referenced_field)
                    if not table1.uniques:
                        table1.uniques = []
                    table1.uniques.append(Unique(name='one_to_one_constr', unique_fields=[referenced_field]))
                elif rel_type == "ONE-TO-MANY":
                    create_fk(master=table2, slave=table1, reference_field=referenced_field)

        return v


def create_fk_many_to_many(master, slave, already_existent_field=None):
    fk_name = already_existent_field
    fk = ForeignKey(field=fk_name, references=slave.table_name, reference_field=slave.primary_key)

    if not master.foreign_keys:
        master.foreign_keys = []

    master.foreign_keys.append(fk)


# theoretically bad design, changing variables passed by reference.. there should be another way
def create_fk(master, slave, reference_field):
    fk_name = f"{slave.table_name}_fk"
    fk = ForeignKey(field=fk_name, references=slave.table_name, reference_field=reference_field)

    fk_field = Field(name=f"{slave.table_name}_fk", type="integer", nullable=False)
    master.fields.append(fk_field)

    if not master.foreign_keys:
        master.foreign_keys = []

    master.foreign_keys.append(fk)
