from typing import List
from utils import get_project_root
import abc


class Generator(abc.ABC):
    def __init__(self):
        self.project_root_dir = get_project_root()

    @abc.abstractmethod
    def generate(self):
        pass


class ResourceBasedGenerator(Generator):
    def __init__(self, resources: List[dict]):
        super().__init__()
        self.resources = resources

    @abc.abstractmethod
    def generate(self):
        pass
