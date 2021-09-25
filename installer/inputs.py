import json
from functools import lru_cache
from typing import Dict, List

from ruamel.yaml import YAML

from .architecture import CONFIG_DIR, SCHEMAS_DIR
from .models import Profile, Service

yaml = YAML(typ="safe")


@lru_cache()
def get_yml(name: str):
    with CONFIG_DIR.joinpath(f"{name}.yml").open() as f:
        return yaml.load(f)


@lru_cache()
def get_json(name: str):
    with SCHEMAS_DIR.joinpath(f"{name}.schema.json").open() as f:
        return json.load(f)


@lru_cache()
def get_services():
    services_data = get_yml("services")
    return [Service(**x) for x in services_data]


@lru_cache()
def get_profiles():
    profiles_data = get_yml("profiles")
    return [Profile(**x) for x in profiles_data]


@lru_cache()
def get_auths() -> Dict[str, List[str]]:
    return get_yml("auths")
