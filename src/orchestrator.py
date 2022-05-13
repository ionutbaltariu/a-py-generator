from SQLAlchemyGenerator import SQLAlchemyGenerator
from PydanticGenerator import PydanticGenerator
from FastAPIGenerator import FastAPIGenerator
from SQLGenerator import SQLGenerator
from DockerGenerator import DockerGenerator
from RelationshipHandler import RelationshipHandler
from view import Input

resources = [
    {
        "name": "Book",
        "table_name": "Books",
        "fields": [
            {
                "name": "isbn",
                "type": "string",
                "length": 100,
                "nullable": False
            },
            {
                "name": "title",
                "type": "string",
                "length": 100,
                "nullable": False
            },
            {
                "name": "year_of_publishing",
                "type": "integer",
                "nullable": False
            }
        ],
        "primary_key": "isbn",
        "relationships": [
            {
                "type": "MANY-TO-MANY",
                "table": "Authors"
            }
        ],
        "uniques": [
            {
                "name": "books_un_1",
                "unique_fields": [
                    "title",
                    "year_of_publishing"
                ]
            }
        ]
    },
    {
        "name": "Author",
        "table_name": "Authors",
        "fields": [
            {
                "name": "author_id",
                "type": "integer",
                "nullable": False
            },
            {
                "name": "first_name",
                "type": "string",
                "length": 100,
                "nullable": False
            },
            {
                "name": "last_name",
                "type": "string",
                "length": 100,
                "nullable": False
            }
        ],

        "primary_key": "author_id",
    }
]

if __name__ == "__main__":
    res = {"resources": resources}
    r = RelationshipHandler(Input(**res).resources)
    r.execute()
    resources = [resource.dict() for resource in r.resources]

    sqlalchemy_generator = SQLAlchemyGenerator(resources)
    pydantic_generator = PydanticGenerator(resources)
    fastapi_generator = FastAPIGenerator(resources)
    sql_generator = SQLGenerator(resources)
    docker_generator = DockerGenerator()

    docker_generator.generate()
    sql_generator.generate()
    sqlalchemy_generator.generate()
    pydantic_generator.generate()
    fastapi_generator.generate()
