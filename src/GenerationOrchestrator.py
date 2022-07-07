from utils import correct_pipreqs_output
from view import Input
from PydanticGenerator import PydanticGenerator
from RelationshipHandler import RelationshipHandler
from SQLAlchemyGenerator import SQLAlchemyGenerator
from MongoGenerator import MongoGenerator
from DockerComposeGenerator import DockerComposeGenerator
from FastAPIGenerator import FastAPIGenerator
from SQLGenerator import SQLGenerator
from RequirementsGenerator import RequirementsGenerator
from StructureGenerator import StructureGenerator
from DockerfileGenerator import DockerfileGenerator


class GenerationOrchestrator:
    def __init__(self, generation_metadata: Input,
                 generation_id: str, project_root: str,
                 python_interpreter: str = "python3"):
        """
        :param generation_metadata: the input of the user
        :param generation_id: the identifier of the generation, used to group the source code in a directory
        :param project_root: the path of the project - this is the place where the folders that contain the
        generated code will be available
        :param python_interpreter: the python interpreter that will be used (python / python3)
        """
        self.generation_metadata = generation_metadata
        self.generation_id = generation_id
        self.project_root = project_root
        self.python_interpreter = python_interpreter

    def generate(self):
        """
        Orchestrator method that parses and validates the relationships as a first step. In case of success, proceeds
        with the construction of the generator list that is to be used in the current generation process. As a final
        step, it calls the 'generate' method of every chosen generator, thus triggering the creation of generated
        source code files on the disk.
        """
        r = RelationshipHandler(self.generation_metadata.resources)
        r.execute()
        resources = [resource.dict() for resource in r.resources]
        generators = []
        options = self.generation_metadata.options
        db_options = options.database_options

        generators.append(StructureGenerator(self.generation_id))

        if options.run_main_app_in_container:
            generators.append(DockerfileGenerator(resources, self.generation_id, options))

        generators.append(DockerComposeGenerator(resources, self.generation_id, options))

        if db_options.db_type == "MariaDB":
            generators.append(SQLAlchemyGenerator(resources, self.generation_id, options))
            generators.append(SQLGenerator(resources, self.generation_id))
        else:
            generators.append(MongoGenerator(resources, self.generation_id, options))

        generators.append(PydanticGenerator(resources, self.generation_id))
        generators.append(FastAPIGenerator(resources, self.generation_id, options))
        generators.append(RequirementsGenerator(self.generation_id, self.python_interpreter))

        for generator in generators:
            generator.generate()

        correct_pipreqs_output(self.project_root, self.generation_id, db_options.db_type)