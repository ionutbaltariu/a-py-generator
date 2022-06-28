import os


def workaround(project_root: str, generation_id: str, db_type: str):
    requirements_txt = os.path.join(project_root, generation_id, "src", "requirements.txt")
    with open(requirements_txt, "r") as f:
        content = f.read()
        content = content.replace("fastapi_cache==0.1.0", "fastapi-cache2==0.1.8")
        if db_type == "MariaDB":
            content += "mysql-connector-python==8.0.27"

    with open(requirements_txt, "w") as f:
        f.write(content)