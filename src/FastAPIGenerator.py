from utils import read_template_from_file, write_to_file
from Generator import ResourceBasedGenerator
from typing import List


class FastAPIGenerator(ResourceBasedGenerator):
    def __init__(self, resources: List[dict], generation_uid):
        super().__init__(resources, generation_uid)

    def create_utils_file(self, resources: List[dict]):
        utils_template = read_template_from_file(f'{self.project_root_dir}/templates/utils.jinja2')
        utils_code = utils_template.render(resources=resources)
        write_to_file(f'{self.generation_path}/utils.py', utils_code)

    def create_routers(self, resources: List[dict]):
        router_template = read_template_from_file(f'{self.project_root_dir}/templates/router.jinja2')

        for resource in resources:
            router_code = router_template.render(entity=resource)
            write_to_file(f'{self.generation_path}/{resource["name"].lower()}_router.py', router_code)

    def create_main_app(self, resources: List[dict]):
        entrypoint_template = read_template_from_file(f'{self.project_root_dir}/templates/fastapi_entrypoint.jinja2')
        entrypoint_code = entrypoint_template.render(resources=resources)
        write_to_file(f'{self.generation_path}/api.py', entrypoint_code)

        # TODO: separate in different function and add configuration of port, host etc

        main_template = read_template_from_file(f'{self.project_root_dir}/templates/main_fastapi.jinja2')
        main_code = main_template.render(resources=resources)
        write_to_file(f'{self.generation_path}/main.py', main_code)

    def generate(self):
        self.create_utils_file(self.resources)
        # TODO: add errors for each entity (replace in jinja template as well)
        self.create_routers(self.resources)
        self.create_main_app(self.resources)
