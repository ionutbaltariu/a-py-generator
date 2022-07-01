from Generator import ResourceBasedGenerator
from view import Options


class MongoGenerator(ResourceBasedGenerator):
    def __init__(self, resources, generation_uid: str, options: Options):
        """
        :param resources: the list of resources defined by the user
        :param generation_uid: the identifier of the generation, used to group the source code in a directory
        :param options: the document containing the settings of the generated application (as a Pydantic model)
        """
        super().__init__(resources, generation_uid)
        self.username = options.database_options.db_username
        self.password = options.database_options.db_password
        self.main_app_in_container = options.run_main_app_in_container
        self.mongo_model_template = self.read_template_from_file('model_mongo.jinja2')

    def generate(self) -> None:
        """
        Creates the model.py file that contains methods that will be used to communicate with the MongoDB server.
        """
        model_code = self.mongo_model_template.render(entities=self.resources,
                                                      username=self.username,
                                                      password=self.password,
                                                      port=27017,
                                                      main_app_in_container=self.main_app_in_container)
        self.write_to_src('model.py', model_code)
