import subprocess
from typing import List
from Generator import Generator


def execute_bash_commands(bash_commands: List[str]):
    """
    Method that can be used to execute bash commands.
    """
    for command in bash_commands:
        subprocess.call(command.split(), stdout=subprocess.PIPE)


class RequirementsGenerator(Generator):
    def __init__(self, generation_uid):
        """
        :param generation_uid: the identifier of the generation, used to group the source code in a directory
        """
        super().__init__(generation_uid)

    def generate(self) -> None:
        """
        Executes a system command that installs pipreqs and then uses it in order to generate the requirements.
        """
        execute_bash_commands(["python3 -m pip install pipreqs", f"pipreqs {self.source_code_path}"])
