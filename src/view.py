import networkx.exception
from pydantic import BaseModel, constr, validator
from typing import List, Optional, Literal
from networkx import DiGraph, find_cycle

ONLY_ALPHA_ERR = '{} must ony contain alphabet characters.'


class Field(BaseModel):
    name: constr(min_length=1, max_length=64)
    type: constr(min_length=1, max_length=64)
    length: Optional[int]
    nullable: bool


class Unique(BaseModel):
    name: constr(min_length=1, max_length=64)
    unique_fields: List[constr(min_length=1, max_length=64)]


class Relationship(BaseModel):
    type: Literal["ONE-TO-ONE", "ONE-TO-MANY", "MANY-TO-ONE", "MANY-TO-MANY"]
    table: str


class ForeignKey(BaseModel):
    field: constr(min_length=1, max_length=64)
    references: constr(min_length=1, max_length=64)


class Resource(BaseModel):
    name: constr(min_length=1, max_length=64)
    table_name: constr(min_length=1, max_length=64)
    fields: List[Field]
    primary_key: constr(min_length=1, max_length=64)
    uniques: Optional[List[Unique]]
    relationships: Optional[List[Relationship]]
    foreign_keys: Optional[List[ForeignKey]]

    @validator('name')
    def resource_name_must_be_pure_string(cls, v):
        if not v.replace('_', '').isalpha():
            raise ValueError(ONLY_ALPHA_ERR.format("Resource name"))
        return v

    @validator('table_name')
    def table_name_must_be_pure_string(cls, v):
        if not v.replace('_', '').isalpha():
            raise ValueError(ONLY_ALPHA_ERR.format("Table name"))
        return v

    # @validator('fields', pre=True)
    # def field_name_must_be_pure_string(cls, v):
    #     fieldnames = [field["name"] for field in v]
    #     print(fieldnames)
    #     for fieldname in fieldnames:
    #         if not fieldname.replace('_', '').isalpha():
    #             print('was here')
    #             raise ValueError("A field's name can only contain alphabetic characters and '_'.")
    #     return v

    @validator('primary_key')
    def primary_key_must_be_in_fields(cls, v, values):
        fieldnames = [field.name for field in values["fields"]]

        if v not in fieldnames:
            raise ValueError(f"Primary key `{v}` should be one of the input fields.")
        return v

    @validator('uniques')
    def unique_keys_must_be_in_fields(cls, v, values):
        fieldnames = [field.name for field in values["fields"]]

        for unique_constr in v:
            if not unique_constr.name.replace('_', '').isalnum():
                raise ValueError(
                    "The unique constraint name can only contain alphanumeric characters, numbers and '_'.")
            for unique_field in unique_constr.unique_fields:
                if unique_field not in fieldnames:
                    raise ValueError(f"Unique `{unique_constr.name}` contains a field that was not declared:"
                                     f" `{unique_field}`")
        return v


class Resources(BaseModel):
    resources: List[Resource]

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
                break

            for relation in resource.relationships:
                if relation.table == resource.table_name:
                    raise ValueError("A table cannot have a relationship with itself.")
                elif relation.table not in tables_names:
                    raise ValueError(f"Table '{resource.table_name}' has a relationship with a table that does not "
                                     f"exist in the given list of resources.")

                relationships.add_edge(resource.table_name, relation.table, weight=relation.type)

        try:
            cycle = find_cycle(relationships)
            cycle = ' -> '.join([f"({x[0]}, {x[1]})" for x in cycle])
            raise ValueError(f"There are circular relationships in the given list of resources. Please revise: {cycle}")
        except networkx.exception.NetworkXNoCycle:
            # there were no cycles and the list of resources can be updated to contain the new foreign keys and eventual
            # link tables (many-to-many)
            for table1, table2, weight in relationships.edges(data=True):
                rel_type = weight["weight"]
                table1 = list(filter(lambda x: x.table_name == table1, v))[0]
                table2 = list(filter(lambda x: x.table_name == table2, v))[0]

                if rel_type == "MANY-TO-MANY":
                    fields = [Field(name=f"{table1.primary_key}", type="integer", nullable=False),
                              Field(name=f"{table2.primary_key}", type="integer", nullable=False)]
                    table_name = f"{table1.table_name}_{table2.table_name}"
                    # TODO: when support for composite primary keys will be added, also change here
                    v.append(
                        Resource(name=table_name, table_name=table_name, fields=fields, primary_key=table1.primary_key))
                elif rel_type == "ONE_TO_ONE" or rel_type == "MANY_TO_ONE":
                    fk = ForeignKey(field=f"{table2.table_name}_fk", references=table2.primary_key)
                    if table1.foreign_keys:
                        table1.foreign_keys.append(fk)
                    else:
                        table1.foreign_keys = [fk]
                else:
                    fk = ForeignKey(field=f"{table1.table_name}_fk", references=table1.primary_key)
                    if table2.foreign_keys:
                        table2.foreign_keys.append(fk)
                    else:
                        table2.foreign_keys = [fk]

        return v
