import os
from typing import List
from utils import get_project_root
import abc


class Generator(abc.ABC):
    def __init__(self, generation_uid):
        self.project_root_dir = get_project_root()
        self.__generation_uid = generation_uid
        self.generation_path = f'{self.project_root_dir}/{self.__generation_uid}'

        if not os.path.exists(self.generation_path):
            os.mkdir(self.generation_path)

    @abc.abstractmethod
    def generate(self):
        pass


class ResourceBasedGenerator(Generator):
    def __init__(self, resources: List[dict], generation_uid):
        super().__init__(generation_uid)
        self.resources = resources

    @abc.abstractmethod
    def generate(self):
        pass
