import io
import os
import uuid
import zipfile
from fastapi import FastAPI, Response
from pydantic import BaseModel
from GenerationOrchestrator import GenerationOrchestrator
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


class Error(BaseModel):
    error_code: int
    error_source: str
    error_reason: str


def zip_generated_code(path: str) -> Response:
    """
    Zips everything at the given path (recursively) and returns an HTTP response containing the zip file.

    :param path: the path of the directory that is to be zipped
    """
    s = io.BytesIO()
    with zipfile.ZipFile(s, 'w') as zip_file:
        for root, dirs, files in os.walk(path):
            for file in files:
                zip_file.write(os.path.join(root, file),
                               os.path.relpath(os.path.join(root, file), os.path.join(path, '..')))

        resp = Response(s.getvalue(),
                        media_type="application/x-zip-compressed",
                        headers={
                            'Content-Disposition': f'attachment;filename=result.zip',
                        },
                        status_code=200)

        return resp


@app.post("/api/generate/")
def generate_app(generation_metadata: Input) -> Response:
    """
    Method that is triggered at the HTTP POST on the /api/generate route.

    :param generation_metadata: the Pydantic model that represents the input (formal description of resources)
    """
    generation_id = str(uuid.uuid4())
    orchestrator = GenerationOrchestrator(generation_metadata, generation_id, project_root)

    try:
        orchestrator.generate()
        response = zip_generated_code(os.path.join(project_root, generation_id))
    except Exception as e:
        response = Response(status_code=500, media_type="application/json",
                            content=Error(error_code=500,
                                          error_source=str(e),
                                          error_reason="EXCEPTION"))

    return response
