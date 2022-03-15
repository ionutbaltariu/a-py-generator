[
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
                "name": "id",
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
        "primary_key": "id"
    }
]