import uuid
from pathlib import Path
from GenerationOrchestrator import GenerationOrchestrator
from view import Input

metadata = {
    "resources": [
        {
            "name": "Customer",
            "table_name": "Customers",
            "fields": [
                {
                    "name": "custid",
                    "type": "integer",
                    "nullable": False
                },
                {
                    "name": "name",
                    "type": "string",
                    "length": 45,
                    "nullable": True
                },
                {
                    "name": "address",
                    "type": "string",
                    "length": 40,
                    "nullable": True
                },
                {
                    "name": "city",
                    "type": "string",
                    "length": 30,
                    "nullable": True
                },
                {
                    "name": "state",
                    "type": "string",
                    "length": 2,
                    "nullable": True
                },
                {
                    "name": "zip",
                    "type": "string",
                    "length": 9,
                    "nullable": True
                },
                {
                    "name": "area",
                    "type": "integer",
                    "nullable": True
                },
                {
                    "name": "phone",
                    "type": "string",
                    "length": 9,
                    "nullable": True
                },
                {
                    "name": "repid",
                    "type": "integer",
                    "nullable": False
                },
                {
                    "name": "creditlimit",
                    "type": "decimal",
                    "nullable": True
                }
            ],
            "primary_key": "custid",
            "relationships": [
                {
                    "type": "ONE-TO-MANY",
                    "table": "Ord",
                    "reference_field": "custid"
                }
            ],
            "options": {
                "api_caching_enabled": True
            }
        },
        {
            "name": "Order",
            "table_name": "Ord",
            "fields": [
                {
                    "name": "ordid",
                    "type": "integer",
                    "nullable": False
                },
                {
                    "name": "total",
                    "type": "decimal",
                    "nullable": True
                },
                {
                    "name": "totaltva",
                    "type": "decimal",
                    "nullable": True
                }
            ],
            "primary_key": "ordid",
            "relationships": [
                {
                    "type": "ONE-TO-MANY",
                    "table": "Items",
                    "reference_field": "ordid"
                }
            ]
        },
        {
            "name": "Product",
            "table_name": "Products",
            "fields": [
                {
                    "name": "prodid",
                    "type": "integer",
                    "nullable": False
                },
                {
                    "name": "descrip",
                    "type": "string",
                    "length": 30,
                    "nullable": True
                },
                {
                    "name": "vat",
                    "type": "decimal",
                    "nullable": True
                },
                {
                    "name": "exp_date",
                    "type": "date",
                    "nullable": True
                }
            ],
            "primary_key": "prodid",
            "relationships": [
                {
                    "type": "ONE-TO-MANY",
                    "table": "Items",
                    "reference_field": "prodid"
                }
            ]
        },
        {
            "name": "Item",
            "table_name": "Items",
            "fields": [
                {
                    "name": "itemid",
                    "type": "integer",
                    "nullable": False
                },
                {
                    "name": "actualprice",
                    "type": "decimal",
                    "nullable": True
                },
                {
                    "name": "qty",
                    "type": "integer",
                    "nullable": True
                },
                {
                    "name": "itemtot",
                    "type": "decimal",
                    "nullable": True
                },
                {
                    "name": "tva",
                    "type": "decimal",
                    "nullable": True
                },
                {
                    "name": "itemgen",
                    "type": "decimal",
                    "nullable": True
                },
                {
                    "name": "guarantee",
                    "type": "integer",
                    "nullable": True
                },
                {
                    "name": "exp_date",
                    "type": "date",
                    "nullable": True
                }
            ],
            "primary_key": "itemid"
        }
    ],
    "options": {
        "database_options": {
            "db_type": "MariaDB",
            "db_port": 27017
        },
        "run_main_app_in_container": False
    }
}


if __name__ == "__main__":
    project_root = Path(__file__).parent.parent
    generation_metadata = Input(**metadata)
    generation_id = str(uuid.uuid4())
    orchestrator = GenerationOrchestrator(generation_metadata, generation_id, project_root)
    orchestrator.generate()

