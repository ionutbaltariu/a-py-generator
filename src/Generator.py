import abc
import os
from pathlib import Path
from typing import List
from jinja2 import Template


class Generator(abc.ABC):
    def __init__(self, generation_uid: str):
        """
        :param generation_uid: the identifier of the current generation process (used as a name for the directory
        that will contain the generated code)
        """
        self.project_root_dir = Path(__file__).parent.parent
        self.__generation_uid = generation_uid
        self.generation_path = os.path.join(self.project_root_dir, self.__generation_uid)
        self.source_code_path = os.path.join(self.generation_path, 'src')

    @abc.abstractmethod
    def generate(self):
        """
        Abstract method that will be implemented in the classes that inherit the 'Generator' class.
        """
        pass

    def read_template_from_file(self, template_name: str) -> Template:
        """
        Concrete method that reads the jinja2 template and returns an object represting the template.

        :param template_name: the name of the template file (including the extention)
        """
        with open(os.path.join(self.project_root_dir, 'templates', template_name), 'r') as f:
            return Template(f.read(), trim_blocks=True, lstrip_blocks=True)

    def write_to_src(self, file_name: str, content: str) -> None:
        """
        Method that creates a file in the 'src' subdirectory of the generated code parent directory.

        :param file_name: the name of the file that is to be created, including the extension
        :param content: the content of the file (generated code)
        """
        with open(os.path.join(self.source_code_path, file_name), 'w', encoding='utf-8') as gen_f:
            gen_f.write(content)

    def write_to_gen_path(self, file_name: str, content: str) -> None:
        """
        Method that creates a file in th generated code parent directory.

        :param file_name: the name of the file that is to be created, including the extension
        :param content: the content of the file (generated code)
        """
        with open(os.path.join(self.generation_path, file_name), 'w', encoding='utf-8') as gen_f:
            gen_f.write(content)


class ResourceBasedGenerator(Generator):
    def __init__(self, resources: List[dict], generation_uid: str):
        super().__init__(generation_uid)
        self.resources = resources

    @abc.abstractmethod
    def generate(self):
        """
        Abstract method that will be implemented in the classes that inherit the 'ResourceBasedGenerator' class.
        """
        pass
