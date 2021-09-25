from contextlib import contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory

from jinja2 import Environment, FileSystemLoader, select_autoescape

from .architecture import TEMPLATES_DIR
from .aws import get_secrets
from .cli.exceptions import SecretsNotFoundError
from .controller import get_commands, get_labels
from .inputs import get_services
from .models import Profile, Service


@contextmanager
def profile_context(profile: Profile):
    with TemporaryDirectory() as tmp_folder:
        build_profile(profile, tmp_folder)
        yield Path(tmp_folder) / f"{profile.name}.yml"


def build_profile(profile: Profile, folder: str):
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
    Path(folder).joinpath(f"{profile.name}.yml").write_text(output)

    for service in services:
        if service.secrets:
            build_env_files(service, folder)


def build_env_files(service: Service, tmp_folder: str):
    secrets = get_secrets(service)
    if not secrets:
        raise SecretsNotFoundError(service)
    env_content = "\n".join(secrets)
    Path(tmp_folder).joinpath(f"{service.name}.env").write_text(env_content)
