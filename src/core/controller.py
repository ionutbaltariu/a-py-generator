from typing import List

import uvicorn
from fastapi import FastAPI
from view import Resource

app = FastAPI()


@app.post("/api/generate")
def generate(resource: List[Resource]):
    return {"is_valid": "yes"}


if __name__ == "__main__":
    uvicorn.run("controller:app", host='0.0.0.0', port=8002, reload=True, debug=True)
