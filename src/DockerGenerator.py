from utils import read_template_from_file, write_to_file
from Generator import Generator


class DockerGenerator(Generator):
    def __init__(self, generation_uid):
        super().__init__(generation_uid)

    def generate(self):
        docker_compose_template = read_template_from_file(f'{self.project_root_dir}/templates/docker_compose.jinja2')
        write_to_file(f'{self.generation_path}/docker-compose.yml',
                      docker_compose_template.render())
