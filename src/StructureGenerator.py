import os
from Generator import Generator


class StructureGenerator(Generator):
    def __init__(self, generation_uid):
        super().__init__(generation_uid)

    def generate(self):
        src_path = os.path.join(self.generation_path, 'src')

        if not os.path.exists(self.generation_path):
            os.mkdir(self.generation_path)

        if not os.path.exists(src_path):
            os.mkdir(src_path)
