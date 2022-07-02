import subprocess
from typing import List
from Generator import Generator


def execute_system_commands(bash_commands: List[str]):
    """
    Method that can be used to execute bash commands.
    """
    for command in bash_commands:
        subprocess.call(command.split(), stdout=subprocess.PIPE, shell=True)


class RequirementsGenerator(Generator):
    def __init__(self, generation_uid, python_interpreter: str):
        """
        :param generation_uid: the identifier of the generation, used to group the source code in a directory
        :param python_interpreter: the python interpreter that will be used
        """
        self.python_interpreter = python_interpreter
        super().__init__(generation_uid)

    def generate(self) -> None:
        """
        Executes a system command that installs pipreqs and then uses it in order to generate the requirements.
        """
        execute_system_commands([f"{self.python_interpreter} -m pip install pipreqs",
                                 f"pipreqs {self.source_code_path}"])
