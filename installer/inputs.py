import json
from functools import lru_cache
from pathlib import Path

from ruamel.yaml import YAML

from .architecture import CONFIG_DIR, SCHEMAS_DIR

yaml = YAML(typ="safe")


@lru_cache
def get_yml(name: str):
    with CONFIG_DIR.joinpath(f"{name}.yml").open() as f:
        return yaml.load(f)


@lru_cache
def get_json(name: str):
    with SCHEMAS_DIR.joinpath(f"{name}.schema.json").open() as f:
        return json.load(f)
