import io
import os
import zipfile
import uuid
from fastapi import FastAPI, Response
from PydanticGenerator import PydanticGenerator
from RelationshipHandler import RelationshipHandler
from SQLAlchemyGenerator import SQLAlchemyGenerator
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
    generation_id = uuid.uuid4()
    r = RelationshipHandler(generation_metadata.resources)
    r.execute()
    resources = [resource.dict() for resource in r.resources]

    sqlalchemy_generator = SQLAlchemyGenerator(resources, generation_id)
    pydantic_generator = PydanticGenerator(resources, generation_id)
    fastapi_generator = FastAPIGenerator(resources, generation_id)
    sql_generator = SQLGenerator(resources, generation_id)
    docker_generator = DockerGenerator(generation_id)
    requirements_generator = RequirementsGenerator(generation_id)

    docker_generator.generate()
    sql_generator.generate()
    sqlalchemy_generator.generate()
    pydantic_generator.generate()
    fastapi_generator.generate()
    requirements_generator.generate()

    return zipfiles(f'{get_project_root()}/{generation_id}')
