import json
from generate_db_connection import generate_connection
from generate_sql import generate_db_create_code
from generate_docker_files import generate_docker_compose
from generate_models import generate_infrastructure
from generate_fastapi import generate_fastapi_code
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
                "type": "ONE-TO-ONE",
                "table": "authors"
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
    shapeshift_resources = Input(**res).resources
    resources = [resource.dict() for resource in shapeshift_resources]

    # TODO: chain of responsibility
    generate_connection()
    generate_db_create_code(json.dumps(resources))
    generate_docker_compose()
    generate_infrastructure(json.dumps(resources))
    generate_fastapi_code(resources)
