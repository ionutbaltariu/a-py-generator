from dataclasses import dataclass
from typing import List
from utils import read_template_from_file, write_to_file
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
    def __init__(self, resources: List[dict], generation_path):
        super().__init__(resources, generation_path)

    def generate(self) -> None:
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

        pydantic_template = read_template_from_file(f'{self.project_root_dir}/templates/pydantic.jinja2')
        pydantic_code = pydantic_template.render(resources=resources)
        write_to_file(f'{self.generation_path}/view.py', pydantic_code)


