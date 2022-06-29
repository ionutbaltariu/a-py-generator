import uuid
import argparse
import json
import os
from json import JSONDecodeError
from pathlib import Path
from GenerationOrchestrator import GenerationOrchestrator
from view import Input
parser = argparse.ArgumentParser(description='A-py-generator parsers.')
parser.add_argument('--input-json', help='An absolute path that indicates the JSON '\
                                         'wanted to be used as input for the app.',
                    type=str, required=True)


if __name__ == "__main__":
    args = parser.parse_args()
    input_path = args.input_json
    if not os.path.exists(input_path):
        print("Please provide a valid path to the input!")
    elif not os.path.splitext(input_path)[1] == ".json":
        print("The path was valid but the file is not a json!")
    else:
        with open(input_path, "r") as input_file:
            try:
                metadata = json.loads(input_file.read())
                project_root = Path(__file__).parent.parent
                generation_metadata = Input(**metadata)
                generation_id = str(uuid.uuid4())
                print(f"Will generate the code into the folder {generation_id}.")
                orchestrator = GenerationOrchestrator(generation_metadata, generation_id, project_root)
                orchestrator.generate()
            except JSONDecodeError:
                print("The provided path is correct but the JSON at that path is invalid.")

