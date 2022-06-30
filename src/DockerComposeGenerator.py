from Generator import ResourceBasedGenerator
from typing import List
from view import Options


class DockerComposeGenerator(ResourceBasedGenerator):
    def __init__(self, resources: List[dict], generation_uid, options: Options):
        """
        :param resources: the list of resources defined by the user
        :param generation_uid: the identifier of the generation, used to group the source code in a directory
        :param options: the document containing the settings of the generated application (as a Pydantic model)
        """
        super().__init__(resources, generation_uid)
        self.redis_needed = False
        self.application_port = options.application_port
        self.docker_compose_template = self.read_template_from_file('docker_compose.jinja2')

        for resource in resources:
            if resource.get("options").get("api_caching_enabled"):
                self.redis_needed = True
                break

        self.db_options = options.database_options
        self.main_app_in_container = options.run_main_app_in_container

    def generate(self):
        """
        The method triggers the generation of the docker-compose.yml file. It instantiates the template and then
        saves the resulted code on the disk.
        """
        docker_compose_code = self.docker_compose_template.render(redis_needed=self.redis_needed,
                                                                  options=self.db_options,
                                                                  application_port=self.application_port,
                                                                  main_app_in_container=self.main_app_in_container)
        self.write_to_gen_path('docker-compose.yml', docker_compose_code)
