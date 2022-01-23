from pydantic import BaseModel, constr, validator
from typing import List, Optional

ONLY_ALPHA_ERR = '{} must ony contain alphabet characters.'


class Field(BaseModel):
    name: constr(min_length=1, max_length=32)
    type: constr(min_length=1, max_length=32)
    length: Optional[int]
    nullable: bool


class Unique(BaseModel):
    name: constr(min_length=1, max_length=32)
    unique_fields: List[constr(min_length=1, max_length=32)]


class Resource(BaseModel):
    name: constr(min_length=1, max_length=32)
    table_name: constr(min_length=1, max_length=32)
    fields: List[Field]
    primary_key: constr(min_length=1, max_length=32)
    uniques: Optional[List[Unique]]

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
                raise ValueError("The unique constraint name can only contain alphanumeric characters, numbers and '_'.")
            for unique_field in unique_constr.unique_fields:
                if unique_field not in fieldnames:
                    raise ValueError(f"Unique `{unique_constr.name}` contains a field that was not declared:"
                                     f" `{unique_field}`")
        return v
