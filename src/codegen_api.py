import io
import os
import zipfile
import uuid
from fastapi import FastAPI, Response
from PydanticGenerator import PydanticGenerator
from RelationshipHandler import RelationshipHandler
from SQLAlchemyGenerator import SQLAlchemyGenerator
from MongoGenerator import MongoGenerator
from DockerComposeGenerator import DockerComposeGenerator
from FastAPIGenerator import FastAPIGenerator
from SQLGenerator import SQLGenerator
from RequirementsGenerator import RequirementsGenerator
from StructureGenerator import StructureGenerator
from DockerfileGenerator import DockerfileGenerator
from view import Input
from pathlib import Path

project_root = Path(__file__).parent.parent

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
    generators = []
    db_type = generation_metadata.options.database_options.db_type
    db_username = generation_metadata.options.database_options.db_username
    db_password = generation_metadata.options.database_options.db_password
    db_port = generation_metadata.options.database_options.db_port
    application_port = generation_metadata.options.project_metadata.application_port

    generators.append(StructureGenerator(generation_id))
    if db_type == "MariaDB":
        generators.append(SQLAlchemyGenerator(resources, generation_id, db_username, db_password, db_port))
        generators.append(SQLGenerator(resources, generation_id))
    elif db_type == "MongoDB":
        generators.append(MongoGenerator(resources, generation_id, db_username, db_password, db_port))

    generators.append(FastAPIGenerator(resources, generation_id, db_type, application_port))
    generators.append(PydanticGenerator(resources, generation_id))
    generators.append(RequirementsGenerator(generation_id))
    generators.append(DockerfileGenerator(resources, generation_id, application_port))
    generators.append(DockerComposeGenerator(generation_id,
                                             resources,
                                             generation_metadata.options.database_options.dict(),
                                             application_port
                                             ))

    for generator in generators:
        generator.generate()

    # pipreqs does not find mysql connector and fastapi_cache correctly

    workaround(str(generation_id), db_type)

    return zipfiles(os.path.join(project_root, str(generation_id)))


def workaround(generation_id: str, db_type: str):
    requirements_txt = os.path.join(project_root, generation_id, "src", "requirements.txt")
    with open(requirements_txt, "r") as f:
        content = f.read()
        content = content.replace("fastapi_cache==0.1.0", "fastapi-cache2==0.1.8")
        if db_type == "MariaDB":
            content += "mysql-connector-python==8.0.27"

    with open(requirements_txt, "w") as f:
        f.write(content)


#