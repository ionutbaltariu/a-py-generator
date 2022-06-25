from Generator import ResourceBasedGenerator
from typing import List


class FastAPIGenerator(ResourceBasedGenerator):
    def __init__(self, resources: List[dict], generation_uid, type: str):
        super().__init__(resources, generation_uid)
        self.type = type
        self.utils_template = self.read_template_from_file('utils.jinja2')
        self.router_template_mariadb = self.read_template_from_file('router_with_sql.jinja2')
        self.router_template_mongodb = self.read_template_from_file('router_with_mongo.jinja2')
        self.entrypoint_template = self.read_template_from_file('fastapi_entrypoint.jinja2')
        self.main_app_template = self.read_template_from_file('main_fastapi.jinja2')

    def create_utils_file(self, resources: List[dict]):
        utils_code = self.utils_template.render(resources=resources)
        self.write_to_src('utils.py', utils_code)

    def create_routers(self, resources: List[dict]):
        if self.type == "MariaDB":
            router_template = self.router_template_mariadb
        else:
            router_template = self.router_template_mongodb

        for resource in resources:
            caching_enabled = resource.get("options").get("api_caching_enabled")
            router_code = router_template.render(entity=resource, caching_enabled=caching_enabled)
            self.write_to_src(f'{resource["name"].lower()}_router.py', router_code)

    def create_main_app(self, resources: List[dict]):
        entrypoint_code = self.entrypoint_template.render(resources=resources)
        self.write_to_src('api.py', entrypoint_code)

        # TODO: separate in different functions and add configuration of port, host etc

        main_code = self.main_app_template.render(resources=resources)
        self.write_to_src('main.py', main_code)

    def generate(self):
        self.create_utils_file(self.resources)
        # TODO: add errors for each entity (replace in jinja template as well)
        self.create_routers(self.resources)
        self.create_main_app(self.resources)
