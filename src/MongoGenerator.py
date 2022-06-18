from Generator import ResourceBasedGenerator
from utils import read_template_from_file, write_to_file
from uuid import uuid4


class MongoGenerator(ResourceBasedGenerator):
    def __init__(self, resources, generation_uid, username="root", password="example", hostname="localhost",
                 port=27017):
        super().__init__(resources, generation_uid)
        self.username = username
        self.password = password
        self.port = port
        self.hostname = hostname

    def generate(self) -> None:
        model_template = read_template_from_file(f'{self.project_root_dir}/templates/model_mongo.jinja2')
        model_code = model_template.render(entities=self.resources,
                                           username=self.username,
                                           password=self.password,
                                           hostname=self.hostname,
                                           port=self.port)
        write_to_file(f'{self.generation_path}/model.py', model_code)
