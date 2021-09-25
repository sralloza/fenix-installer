import re
import shlex
from typing import List

from click import BadOptionUsage, Context, Option

from ..inputs import get_services
from ..models import Service
from .exceptions import ServiceNotFoundError


def get_service_names() -> List[str]:
    services = get_services()
    return [x.name for x in services]


def get_service_names_with_secrets() -> List[str]:
    services = get_services()
    return [x.name for x in services if x.secrets]


def get_service_by_name(service_name: str) -> Service:
    services = get_services()
    for service in services:
        if service.name == service_name:
            return service
    raise ServiceNotFoundError(service_name)


def shlex_join(split_command):
    """Returns a shell-escaped string from 'split_command'.
    This function is natively available in the shlex module from Python >= 3.8.
    """
    return " ".join(shlex.quote(arg) for arg in split_command)


def check_env(ctx: Context, option: Option, env: List[str]):
    for var in env:
        if not re.search(r"\w+=\w+", var):
            raise BadOptionUsage(
                option.name,
                f"Environment variable {var!r} is not valid (KEY=VALUE)",
                ctx,
            )
    return env
