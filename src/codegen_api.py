import io
import os
import zipfile
import uuid
from fastapi import FastAPI, Response
from PydanticGenerator import PydanticGenerator
from RelationshipHandler import RelationshipHandler
from SQLAlchemyGenerator import SQLAlchemyGenerator
from MongoGenerator import MongoGenerator
from DockerGenerator import DockerGenerator
from FastAPIGenerator import FastAPIGenerator
from SQLGenerator import SQLGenerator
from RequirementsGenerator import RequirementsGenerator
from view import Input
from utils import get_project_root

app = FastAPI(
    title="A Py Generator - Code Generation As A Service",
    description="Generate CRUD code for custom resources, on-demand!",
    version="0.0.1",
    contact={
        "name": "Ionut B.",
        "url": "https://xeno-john.github.io/"
    },
    license_info={
        "name": "GNU General Public License v3.0"
    },
)


def zipfiles(path):
    s = io.BytesIO()
    with zipfile.ZipFile(s, 'w') as zipf:
        for root, dirs, files in os.walk(path):
            for file in files:
                zipf.write(os.path.join(root, file),
                           os.path.relpath(os.path.join(root, file),
                           os.path.join(path, '..')))

        resp = Response(s.getvalue(), media_type="application/x-zip-compressed", headers={
            'Content-Disposition': f'attachment;filename=result.zip'
        })

        return resp


@app.post("/api/generate/")
def read_root(generation_metadata: Input):
    print(generation_metadata)
    generation_id = uuid.uuid4()
    r = RelationshipHandler(generation_metadata.resources)
    r.execute()
    resources = [resource.dict() for resource in r.resources]
    generators = []
    db_type = generation_metadata.options.database_options.db_type

    if db_type == "MariaDB":
        generators.append(SQLAlchemyGenerator(resources, generation_id))
        generators.append(SQLGenerator(resources, generation_id))
    elif db_type == "MongoDB":
        generators.append(MongoGenerator(resources, generation_id))

    generators.append(FastAPIGenerator(resources, generation_id, type=db_type))
    generators.append(PydanticGenerator(resources, generation_id))
    generators.append(DockerGenerator(generation_id))
    generators.append(RequirementsGenerator(generation_id))

    for generator in generators:
        generator.generate()

    return zipfiles(f'{get_project_root()}/{generation_id}')
