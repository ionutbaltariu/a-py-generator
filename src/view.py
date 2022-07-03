from pydantic import BaseModel, constr, validator, Extra, Field
from typing import List, Optional, Literal
from keyword import iskeyword
from config import MAX_RESOURCES_ALLOWED, MAX_STR_LENGTH, PASSWORD_LENGTH, PROJECT_DESCRIPTION_MAX_LENGTH, \
    PROJECT_VERSION_MAX_LENGTH, MAX_WEBSITE_LENGTH


def generic_alphanumeric_validator(element: str, element_name: str) -> None:
    """
    Raises an exception if the given field value is not alphanumeric (it can contain '_')

    :param element: the value of the field that is to be checked
    :param element_name: the name of the checked field
    """
    if not element.replace('_', '').isalnum():
        raise ValueError(f"A(n) {element_name} can only contain alphabetic characters and '_'.")


def generic_keyword_verifier(element: str, element_name: str) -> None:
    """
    Raises an exception if the given field is a Python keyword.

    :param element: the value of the field that is to be checked
    :param element_name: the name of the checked field
    """
    if iskeyword(element):
        raise ValueError(f"A(n) {element_name}  cannot be equivalent to a Python keyword.")


def string_must_not_start_with_number_verifier(element: str, element_name: str) -> None:
    """
    Raises an exception if the given field value begins with a number.

    :param element: the value of the field that is to be checked
    :param element_name: the name of the checked field
    """
    if element[:1].isdigit():
        raise ValueError(f"A(n) {element_name}'s name cannot begin with a number.")


def generic_alphanumeric_and_keyword_validator(element: str, element_name: str) -> None:
    """
    Checks for he validity of a given field value. It must not be a Python keyword, must be alphanumeric with optional
    underscores and must not begin with a number.

    :param element: the value of the field that is to be checked
    :param element_name: the name of the checked field
    """
    generic_keyword_verifier(element, element_name)
    generic_alphanumeric_validator(element, element_name)
    string_must_not_start_with_number_verifier(element, element_name)


class ResourceField(BaseModel, extra=Extra.forbid):
    name: constr(min_length=1, max_length=MAX_STR_LENGTH)
    type: Literal["integer", "string", "decimal", "boolean", "date"]
    length: Optional[int]
    nullable: bool

    @validator('length')
    def length_must_me_reasonable(cls, v, values):
        if v is None:
            return v

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
    name: constr(min_length=1, max_length=MAX_STR_LENGTH)
    unique_fields: List[constr(min_length=1, max_length=MAX_STR_LENGTH)]


class Relationship(BaseModel, extra=Extra.forbid):
    type: Literal["ONE-TO-ONE", "ONE-TO-MANY", "MANY-TO-MANY"]
    table: constr(min_length=1, max_length=MAX_STR_LENGTH)
    reference_field: Optional[constr(min_length=1, max_length=MAX_STR_LENGTH)]
    role: Optional[Literal["Child", "Parent", "JoinTable"]]


class ForeignKey(BaseModel, extra=Extra.forbid):
    field: constr(min_length=1, max_length=MAX_STR_LENGTH)
    references: constr(min_length=1, max_length=MAX_STR_LENGTH)
    reference_field: constr(min_length=1, max_length=MAX_STR_LENGTH)


class DatabaseOptions(BaseModel, extra=Extra.forbid):
    db_type: Literal["MariaDB", "MongoDB"] = Field(default="MariaDB")
    db_username: Optional[constr(min_length=1, max_length=MAX_STR_LENGTH)] = Field(default="root")
    db_password: Optional[constr(min_length=1, max_length=PASSWORD_LENGTH)] = Field(default="generated_password")


class ProjectMetadata(BaseModel, extra=Extra.forbid):
    title: constr(min_length=1, max_length=MAX_STR_LENGTH) = Field(default="Generated Application")
    description: constr(min_length=1,
                        max_length=PROJECT_DESCRIPTION_MAX_LENGTH) = Field(default="Generated with a-py-generator")
    version: constr(min_length=1, max_length=PROJECT_VERSION_MAX_LENGTH) = Field(default="0.0.1")
    creator_name: constr(min_length=1, max_length=MAX_STR_LENGTH) = Field(default="")
    creator_website: constr(min_length=1, max_length=MAX_WEBSITE_LENGTH) = Field(default="")


class Options(BaseModel, extra=Extra.forbid):
    database_options: Optional[DatabaseOptions] = Field(default=DatabaseOptions())
    project_metadata: Optional[ProjectMetadata] = Field(default=ProjectMetadata())
    run_main_app_in_container: bool = Field(default=True)
    application_port: int = Field(default=5555)

    @validator("application_port")
    def validate_port(cls, application_port):
        if application_port > 65535:
            raise ValueError(f"A port can have a maximum value of 65535!")
        elif application_port < 0:
            raise ValueError(f"Please provide a positive number for the port.")
        return application_port


class ResourceOptions(BaseModel, extra=Extra.forbid):
    api_caching_enabled: Optional[bool] = Field(default=False)
    cache_for: Optional[int] = Field(default=60)

    @validator("cache_for")
    def validate_caching_time(cls, cache_for):
        if cache_for < 1 or cache_for > int(3.1536e+7):
            raise ValueError("A resource can be cached for a maximum of a year"
                             " and for a minimum of one second.")
        return cache_for


class Resource(BaseModel, extra=Extra.forbid):
    name: constr(min_length=1, max_length=MAX_STR_LENGTH)
    table_name: constr(min_length=1, max_length=MAX_STR_LENGTH)
    fields: List[ResourceField]
    primary_key: constr(min_length=1, max_length=MAX_STR_LENGTH)
    uniques: Optional[List[Unique]]
    relationships: Optional[List[Relationship]]
    foreign_keys: Optional[List[ForeignKey]]
    options: Optional[ResourceOptions] = Field(default=ResourceOptions())

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
    options: Optional[Options] = Field(default=Options())

    @validator('resources')
    def resource_list_cannot_be_empty(cls, v):
        if (len(v)) == 0:
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
    def check_for_invalid_relationships(cls, v):
        tables_names = [x.table_name for x in v]

        for resource in v:
            # guard for the resources that do not have relationship
            if not resource.relationships:
                continue

            for relation in resource.relationships:
                if relation.reference_field is not None and relation.type == "MANY-TO-MANY":
                    raise ValueError(f"There should not be a referenced field"
                                     f" when the relationship type is 'MANY-TO-MANY'")
                if relation.reference_field is None and relation.type != "MANY-TO-MANY":
                    raise ValueError(f"Please introduce a referenced field in the parent table.")

                if relation.table == resource.table_name:
                    raise ValueError("A table cannot have a relationship with itself.")
                elif relation.table not in tables_names:
                    raise ValueError(f"Table '{resource.table_name}' has a relationship with a table that does not "
                                     f"exist in the given list of resources.")

                if relation.reference_field not in [x.name for x in
                                                    resource.fields] and relation.type != "MANY-TO-MANY":
                    raise ValueError(f"The referenced field should exist in '{resource.table_name}'!")
        return v
