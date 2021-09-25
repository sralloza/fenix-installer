from typing import Iterator

from .architecture import DEFAULT_PROFILE
from .cli.exceptions import ProfileNotFoundError
from .inputs import get_auths, get_profiles
from .models import Profile, Service


def get_commands(service: Service, profile: Profile) -> Iterator[str]:
    commands = service.commands or list()

    if profile.traefik_token and service.name == "traefik":
        commands.append("--pilot.token=" + profile.traefik_token)

    if profile.https:
        commands += service.commands_https

    commands.sort()
    yield from commands


def get_labels(service, profile: Profile) -> Iterator[str]:
    # TODO: if we support TCP, this will break
    if not service.traefik_port or not service.url:
        yield "traefik.enable=false"
        return

    if profile.prod is True and service.url.prod is None:
        return
    if profile.prod is False and service.url.dev is None:
        return

    url = service.url.prod if profile.prod else service.url.dev

    yield f"traefik.http.routers.{service.name}-http.entrypoints=http"
    yield f"traefik.http.routers.{service.name}-http.service={service.service_name or service.name}"

    if service.name == "traefik":
        for auth_id, auth_list in get_auths().items():
            auth_data = ",".join(auth_list)
            yield f"traefik.http.middlewares.{auth_id}.basicauth.removeheader=true"
            yield f"traefik.http.middlewares.{auth_id}.basicauth.users={auth_data}"

        if profile.https:
            yield "traefik.http.middlewares.redirect.redirectscheme.scheme=https"

    if service.auth:
        yield f"traefik.http.routers.{service.name}-http.middlewares={service.auth}"
        if profile.https:
            yield f"traefik.http.routers.{service.name}-https.middlewares={service.auth}"

    if service.traefik_port:
        yield f"traefik.http.services.{service.name}.loadbalancer.server.port={service.traefik_port}"

    or_rules = [f"Host(`{url}`)"]
    if service.default:
        or_rules.append('HostRegexp("{catchall:.*}")')
    if service.path_prefix:
        or_rules = [f"({x} && PathPrefix(`{service.path_prefix}`))" for x in or_rules]
    rules = " || ".join(or_rules)

    common_priority = 30 if service.path_prefix else 20

    if service.default:
        yield f"traefik.http.routers.{service.name}-http.priority=10"
        yield f"traefik.http.routers.{service.name}-http.rule={rules}"
    else:
        yield f"traefik.http.routers.{service.name}-http.priority={common_priority}"
        yield f"traefik.http.routers.{service.name}-http.rule={rules}"

    if profile.https:
        yield f"traefik.http.routers.{service.name}-http.middlewares=redirect"
        yield f"traefik.http.routers.{service.name}-https.entrypoints=https"
        yield f"traefik.http.routers.{service.name}-https.tls.certresolver=letsencrypt"
        yield f"traefik.http.routers.{service.name}-https.tls=true"

        if service.default:
            yield f"traefik.http.routers.{service.name}-https.priority=10"
            yield f"traefik.http.routers.{service.name}-https.rule={rules}"
        else:
            yield f"traefik.http.routers.{service.name}-https.priority={common_priority}"
            yield f"traefik.http.routers.{service.name}-https.rule={rules}"
            yield f"traefik.http.routers.{service.name}-https.service={service.service_name or service.name}"


def get_default_profile() -> Profile:
    for profile in get_profiles():
        if profile.name == DEFAULT_PROFILE:
            return profile
    raise ProfileNotFoundError(DEFAULT_PROFILE)
