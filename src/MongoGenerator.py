from Generator import ResourceBasedGenerator


class MongoGenerator(ResourceBasedGenerator):
    def __init__(self, resources, generation_uid, username="root", password="example", port=27017):
        super().__init__(resources, generation_uid)
        self.username = username
        self.password = password
        self.port = port
        self.mongo_model_template = self.read_template_from_file('model_mongo.jinja2')

    def generate(self) -> None:
        model_code = self.mongo_model_template.render(entities=self.resources,
                                                      username=self.username,
                                                      password=self.password,
                                                      port=self.port)
        self.write_to_src('model.py', model_code)
