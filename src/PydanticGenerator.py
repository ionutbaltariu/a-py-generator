from dataclasses import dataclass
from typing import List
from Generator import ResourceBasedGenerator

pseudocode_to_pydantic = {
    'string': 'constr(min_length=1, max_length={length})',
    'integer': 'int',
    'decimal': 'float',
    'boolean': 'bool',
    'date': 'datetime.date'
}


@dataclass
class PydanticField:
    name: str
    type: str


@dataclass
class PydanticResource:
    name: str
    table_name: str
    primary_key: str
    fields: List[PydanticField]


class PydanticGenerator(ResourceBasedGenerator):
    def __init__(self, resources: List[dict], generation_uid: str):
        """
        :param resources: the list of resources defined by the user
        :param generation_uid: the identifier of the generation, used to group the source code in a directory
        """
        super().__init__(resources, generation_uid)
        self.pydantic_template = self.read_template_from_file('pydantic.jinja2')

    def generate(self) -> None:
        """
        Creates the view.py file that contains all of the Pydantic models of the generated application.
        """
        resources = []
        for resource in self.resources:
            fields = []
            for field in resource["fields"]:
                if field["type"] == "string":
                    field_type = pseudocode_to_pydantic["string"].format(length=field["length"])
                else:
                    field_type = pseudocode_to_pydantic[field["type"]]

                fields.append(PydanticField(field["name"], field_type))
            resources.append(PydanticResource(resource["name"],
                                              resource["table_name"],
                                              resource["primary_key"],
                                              fields))

        pydantic_code = self.pydantic_template.render(resources=resources)
        self.write_to_src('view.py', pydantic_code)


