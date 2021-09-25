from contextlib import contextmanager
from pathlib import Path
from typing import List

import click
from jinja2 import Environment, FileSystemLoader, select_autoescape

from .architecture import FENIX_DIR, TEMPLATES_DIR
from .aws import get_secrets
from .cli.exceptions import SecretsNotFoundError
from .controller import get_commands, get_labels
from .inputs import get_services
from .models import Profile, Service


@contextmanager
def profile_context(profile: Profile, debug: bool):
    created_files = build_profile(profile)
    try:
        yield created_files[0]
    finally:
        if not debug:
            for file in created_files:
                file.unlink()
        else:
            click.secho(
                "WARNING: tmp files are not removed, you must clean them manually!",
                fg="bright_yellow",
            )


def build_profile(profile: Profile) -> List[Path]:
    created_files = []
    services = get_services()
    env = Environment(
        loader=FileSystemLoader(TEMPLATES_DIR),
        autoescape=select_autoescape(["html", "xml"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    template_path = "docker-compose.tmpl"
    template = env.get_template(template_path)
    env_vars = dict(
        services=services,
        profile=profile,
        get_commands=get_commands,
        get_labels=get_labels,
    )
    output = template.render(**env_vars)
    profile_path = FENIX_DIR.joinpath(profile.filepath)
    profile_path.write_text(output)
    created_files.append(profile_path)

    for service in services:
        if service.secrets:
            env_file_path = build_env_files(service)
            created_files.append(env_file_path)
    return created_files


def build_env_files(service: Service) -> Path:
    secrets = get_secrets(service)
    if not secrets:
        raise SecretsNotFoundError(service)
    env_content = "\n".join(secrets)
    env_file_path = FENIX_DIR.joinpath(f"{service.name}.env")
    env_file_path.write_text(env_content)
    return env_file_path
