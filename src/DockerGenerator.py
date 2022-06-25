from Generator import ResourceBasedGenerator
from typing import List


class DockerGenerator(ResourceBasedGenerator):
    def __init__(self, generation_uid, resources: List[dict], database_options):
        super().__init__(resources, generation_uid)
        self.redis_needed = False
        self.docker_compose_template = self.read_template_from_file('docker_compose.jinja2')

        for resource in resources:
            if resource.get("options").get("api_caching_enabled"):
                self.redis_needed = True
                break
        self.options = database_options

    def generate(self):
        docker_compose_code = self.docker_compose_template.render(redis_needed=self.redis_needed, options=self.options)
        self.write_to_gen_path('docker-compose.yml', docker_compose_code)
