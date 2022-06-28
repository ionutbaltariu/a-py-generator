import io
import os
import uuid
import zipfile
from fastapi import FastAPI, Response

from src.GenerationOrchestrator import GenerationOrchestrator
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


def zip_generated_code(path):
    s = io.BytesIO()
    with zipfile.ZipFile(s, 'w') as zip_file:
        for root, dirs, files in os.walk(path):
            for file in files:
                zip_file.write(os.path.join(root, file),
                               os.path.relpath(os.path.join(root, file), os.path.join(path, '..')))

        resp = Response(s.getvalue(), media_type="application/x-zip-compressed", headers={
            'Content-Disposition': f'attachment;filename=result.zip'
        })

        return resp


@app.post("/api/generate/")
def generate_app(generation_metadata: Input):
    generation_id = str(uuid.uuid4())
    orchestrator = GenerationOrchestrator(generation_metadata, generation_id, project_root)
    orchestrator.generate()

    return zip_generated_code(os.path.join(project_root, generation_id))
