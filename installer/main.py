from jinja2 import Environment, FileSystemLoader, select_autoescape

from .controller import get_commands, get_labels, get_profiles, get_services
from .inputs import MANIFESTS_DIR, TEMPLATES_DIR
from .models import Profile
from .schemas import validate_all


def build_profile(profile: Profile):
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
    MANIFESTS_DIR.joinpath(f"{profile.name}.yml").write_text(output)


def build_all_profiles():
    validate_all()
    profiles = get_profiles()
    for profile in profiles:
        if not profile.enabled:
            continue
        build_profile(profile)
