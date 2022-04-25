from utils import read_template_from_file, write_to_file
from Generator import ResourceBasedGenerator
from typing import List


class FastAPIGenerator(ResourceBasedGenerator):
    def __init__(self, resources: List[dict]):
        super().__init__(resources)

    def create_utils_file(self, resources: List[dict]):
        utils_template = read_template_from_file(f'{self.project_root_dir}/templates/utils.jinja2')
        utils_code = utils_template.render(resources=resources)
        write_to_file(f'{self.project_root_dir}/generated/utils.py', utils_code)

    def create_routers(self, resources: List[dict]):
        router_template = read_template_from_file(f'{self.project_root_dir}/templates/router.jinja2')

        for resource in resources:
            router_code = router_template.render(entity=resource)
            write_to_file(f'{self.project_root_dir}/generated/{resource["name"].lower()}_router.py', router_code)

    def create_main_app(self, resources: List[dict]):
        app_template = read_template_from_file(f'{self.project_root_dir}/templates/main_fastapi.jinja2')
        app_code = app_template.render(resources=resources)
        write_to_file(f'{self.project_root_dir}/generated/main.py', app_code)

    def generate(self):
        self.create_utils_file(self.resources)
        # TODO: add errors for each entity (replace in jinja template as well)
        self.create_routers(self.resources)
        self.create_main_app(self.resources)
