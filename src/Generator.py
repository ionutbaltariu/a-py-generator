import abc
import os
from pathlib import Path
from typing import List
from jinja2 import Template


class Generator(abc.ABC):
    def __init__(self, generation_uid: str):
        self.project_root_dir = Path(__file__).parent.parent
        self.__generation_uid = generation_uid
        self.generation_path = os.path.join(self.project_root_dir, self.__generation_uid)
        self.source_code_path = os.path.join(self.generation_path, 'src')

    @abc.abstractmethod
    def generate(self):
        pass

    def read_template_from_file(self, template_name):
        with open(os.path.join(self.project_root_dir, 'templates', template_name), 'r') as f:
            return Template(f.read(), trim_blocks=True, lstrip_blocks=True)

    def write_to_src(self, file_name: str, content: str) -> None:
        with open(os.path.join(self.source_code_path, file_name), 'w', encoding='utf-8') as gen_f:
            gen_f.write(content)

    def write_to_gen_path(self, file_name: str, content: str) -> None:
        with open(os.path.join(self.generation_path, file_name), 'w', encoding='utf-8') as gen_f:
            gen_f.write(content)


class ResourceBasedGenerator(Generator):
    def __init__(self, resources: List[dict], generation_uid):
        super().__init__(generation_uid)
        self.resources = resources

    @abc.abstractmethod
    def generate(self):
        pass
