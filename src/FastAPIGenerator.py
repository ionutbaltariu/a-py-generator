from Generator import ResourceBasedGenerator
from typing import List

datatype_converter = {
    'string': 'str',
    'integer': 'int',
    'decimal': 'float'
}


class FastAPIGenerator(ResourceBasedGenerator):
    def __init__(self, resources: List[dict], generation_uid, db_type: str, application_port: int):
        super().__init__(resources, generation_uid)
        self.type = db_type
        self.application_port = application_port
        self.utils_template = self.read_template_from_file('utils.jinja2')
        self.router_template_mariadb = self.read_template_from_file('router_with_sql.jinja2')
        self.router_template_mongodb = self.read_template_from_file('router_with_mongo.jinja2')
        self.entrypoint_template = self.read_template_from_file('fastapi_entrypoint.jinja2')
        self.main_app_template = self.read_template_from_file('main_fastapi.jinja2')

        self.at_least_one_cached_resource = False

        for resource in self.resources:
            if resource.get("options").get("api_caching_enabled") is True:
                self.at_least_one_cached_resource = True
                break

        for resource in self.resources:
            pk_type = [x for x in resource.get("fields") if x.get("name") == resource.get("primary_key")][0].get("type")
            resource["pk_type"] = datatype_converter[pk_type]

    def create_utils_file(self):
        utils_code = self.utils_template.render(resources=self.resources)
        self.write_to_src('utils.py', utils_code)

    def create_routers(self):
        if self.type == "MariaDB":
            router_template = self.router_template_mariadb
        else:
            router_template = self.router_template_mongodb

        for resource in self.resources:
            caching_enabled = resource.get("options").get("api_caching_enabled")
            router_code = router_template.render(entity=resource, caching_enabled=caching_enabled)
            self.write_to_src(f'{resource["name"].lower()}_router.py', router_code)

    def create_main_app(self):
        entrypoint_code = self.entrypoint_template.render(resources=self.resources,
                                                          caching_enabled=self.at_least_one_cached_resource)
        self.write_to_src('api.py', entrypoint_code)

        # TODO: separate in different functions and add configuration of port, host etc

        main_code = self.main_app_template.render(application_port=self.application_port)
        self.write_to_src('main.py', main_code)

    def generate(self):
        self.create_utils_file()
        # TODO: add errors for each entity (replace in jinja template as well)
        self.create_routers()
        self.create_main_app()
