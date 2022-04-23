from generate_db_connection import generate_connection
from generate_sql import generate_db_create_code
from generate_docker_files import generate_docker_compose
from generate_pydantic import generate_pydantic_models
from generate_fastapi import generate_fastapi_code
from generate_sqlalchemy_models import generate_sqlalchemy_classes
from generate_model_code import generate_model_code
from view import Input
from RelationshipHandler import RelationshipHandler

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
                "type": "ONE-TO-MANY",
                "table": "authors",
                "reference_field": "isbn"
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
        "table_name": "authors",
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

    # TODO: chain of responsibility
    generate_connection()
    generate_db_create_code(resources)
    generate_docker_compose()
    generate_pydantic_models(resources)
    generate_sqlalchemy_classes(resources)
    generate_model_code(resources)
    generate_fastapi_code(resources)
