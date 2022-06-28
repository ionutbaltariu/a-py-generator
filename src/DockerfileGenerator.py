from Generator import ResourceBasedGenerator
from view import Options


class DockerfileGenerator(ResourceBasedGenerator):
    def __init__(self, resources, generation_uid, options: Options):
        super().__init__(resources, generation_uid)
        self.application_port = options.application_port
        self.mongo_model_template = self.read_template_from_file('dockerfile.jinja2')

    def generate(self) -> None:
        dockerfile_code = self.mongo_model_template.render(application_port=self.application_port)
        self.write_to_src('Dockerfile', dockerfile_code)
