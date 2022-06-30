from Generator import ResourceBasedGenerator
from view import Options


class DockerfileGenerator(ResourceBasedGenerator):
    def __init__(self, resources, generation_uid, options: Options):
        """
        :param resources: the list of resources defined by the user
        :param generation_uid: the identifier of the generation, used to group the source code in a directory
        :param options: the document containing the settings of the generated application (as a Pydantic model)
        """
        super().__init__(resources, generation_uid)
        self.application_port = options.application_port
        self.mongo_model_template = self.read_template_from_file('dockerfile.jinja2')

    def generate(self) -> None:
        """
        The method triggers the generation of the Dockerfile. The Dockerfile will be used to deploy the API
        code in a Docker container.
        """
        dockerfile_code = self.mongo_model_template.render(application_port=self.application_port)
        self.write_to_src('Dockerfile', dockerfile_code)
