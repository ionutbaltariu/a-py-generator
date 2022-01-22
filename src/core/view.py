from pydantic import BaseModel, constr, validator
from typing import List, Optional

ONLY_ALPHA_ERR = '{} must ony contain alphabet characters.'


class Field(BaseModel):
    name: constr(min_length=1, max_length=32)
    type: constr(min_length=1, max_length=32)
    length: Optional[int]
    nullable: bool

    @validator('name')
    def field_name_must_be_pure_string(cls, v):
        if not v.replace('_', '').isalpha():
            raise ValueError("A field's name can only contain alphabetic characters and '_'.")
        return v


class Unique(BaseModel):
    name: constr(min_length=1, max_length=32)
    unique_fields: List[constr(min_length=1, max_length=32)]

    @validator('name')
    def unique_name_must_be_alpha(cls, v):
        if not v.replace('_', '').isalnum():
            raise ValueError("The unique constraint name can only contain alphabetic characters, numbers and '_'.")
        return v


class Resource(BaseModel):
    name: constr(min_length=1, max_length=32)
    table_name: constr(min_length=1, max_length=32)
    fields: List[Field]
    primary_key: constr(min_length=1, max_length=32)
    uniques: List[Unique]

    @validator('name')
    def resource_name_must_be_pure_string(cls, v):
        if not v.isalpha():
            raise ValueError(ONLY_ALPHA_ERR.format("Resource name"))
        return v

    @validator('table_name')
    def table_name_must_be_pure_string(cls, v):
        if not v.isalpha():
            raise ValueError(ONLY_ALPHA_ERR.format("Table name"))
        return v

    @validator('primary_key')
    def primary_key_must_be_in_fields(cls, v, values):
        print(values)
        fieldnames = [field.name for field in values["fields"]]

        if v not in fieldnames:
            raise ValueError('Primary key should be one of the given fields.')
        return v

    @validator('uniques')
    def unique_keys_must_be_in_fields(cls, v, values):
        fieldnames = [field.name for field in values["fields"]]

        for unique_constr in v:
            for unique_field in unique_constr.unique_fields:
                if unique_field not in fieldnames:
                    raise ValueError(f"Unique `{unique_constr.name}` contains a field that was not declared:"
                                     f" `{unique_field}`")
        return v
