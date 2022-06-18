import subprocess
from typing import List
from Generator import Generator


def execute_bash_commands(bash_commands: List[str]):
    for command in bash_commands:
        process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
        output, error = process.communicate()

        # TODO: handle error


class RequirementsGenerator(Generator):
    def __init__(self, generation_uid):
        super().__init__(generation_uid)

    def generate(self) -> None:
        execute_bash_commands(["python3 -m pip install pipreqs", f"pipreqs {self.generation_path}"])
