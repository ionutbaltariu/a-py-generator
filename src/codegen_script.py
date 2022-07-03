import uuid
import argparse
import json
import os
import traceback
from json import JSONDecodeError
from pathlib import Path
from GenerationOrchestrator import GenerationOrchestrator
from view import Input

parser = argparse.ArgumentParser(description='A-py-generator parsers.')
parser.add_argument('--input-json',
                    help='An absolute path that indicates the JSON wanted to be used as input for the app.',
                    type=str,
                    required=True)
parser.add_argument('--python-interpreter',
                    help='[Optional] The python interpreter to be used when trying to install pipreqs. Defaults'
                         'to "python3"',
                    type=str,
                    required=False,
                    choices=["python", "python3"])


if __name__ == "__main__":
    args = parser.parse_args()
    input_path = args.input_json
    script_name = __file__.split("/")[-1]
    interpreter = "python3" if (i := args.python_interpreter) is None else i

    if not os.path.exists(input_path):
        print(f"{script_name}: error: Please provide a valid path to the input!")
    elif not os.path.splitext(input_path)[1] == ".json":
        print(f"{script_name}: error: The path was valid but the file is not a json!")
    else:
        with open(input_path, "r") as input_file:
            try:
                metadata = json.loads(input_file.read())
                project_root = Path(__file__).parent.parent
                generation_metadata = Input(**metadata)
                generation_id = str(uuid.uuid4())
                print(f"Will generate the code into the folder {generation_id}.")
                orchestrator = GenerationOrchestrator(generation_metadata, generation_id, project_root, interpreter)
                orchestrator.generate()
                print(f"Finished generating code with the ID {generation_id}.")
            except JSONDecodeError:
                print(f"{script_name}: error: The provided path is correct but the JSON document is invalid.")
            except ValueError:
                print(traceback.format_exc())
            except Exception:
                print(traceback.format_exc())
                print(f"{script_name}: error: An unkown error has occured!")

