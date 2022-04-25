from pathlib import Path

from jinja2 import Template


def get_project_root() -> Path:
    return Path(__file__).parent.parent


def read_template_from_file(path: str) -> Template:
    with open(path, 'r') as f:
        return Template(f.read(), trim_blocks=True, lstrip_blocks=True)


def write_to_file(file: str, content: str) -> None:
    with open(file, 'w', encoding='utf-8') as gen_f:
        gen_f.write(content)
