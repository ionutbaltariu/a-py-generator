import os
from Generator import Generator


class StructureGenerator(Generator):
    def __init__(self, generation_uid):
        """
        :param generation_uid: the identifier of the generation, used to group the source code in a directory
        """
        super().__init__(generation_uid)

    def generate(self):
        """
        Creates two folders, first being the one in which the generated code will be stored, second being the
        'src' directory that will contain generated Python code.
        """
        src_path = os.path.join(self.generation_path, 'src')

        if not os.path.exists(self.generation_path):
            os.mkdir(self.generation_path)

        if not os.path.exists(src_path):
            os.mkdir(src_path)
