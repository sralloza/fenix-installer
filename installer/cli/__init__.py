from typing import List, Optional

import click

from ..architecture import *
from ..schemas import validate_all
from .core import DockerCompose, Secrets
from .utils import check_env, get_service_names, get_service_names_with_secrets

SERVICE_NAMES = get_service_names()
SERVICES_NAMES_WITH_SECRETS = get_service_names_with_secrets()
_S = List[str]

services = click.argument(
    "services", metavar="SERVICES", nargs=-1, type=click.Choice(SERVICE_NAMES)
)
service = click.argument(
    "service", metavar="SERVICE", nargs=1, type=click.Choice(SERVICE_NAMES)
)
service_with_secret = click.argument(
    "service",
    metavar="SERVICE",
    nargs=1,
    type=click.Choice(SERVICES_NAMES_WITH_SECRETS),
)


@click.group(no_args_is_help=True)
def cli():
    pass


@cli.command("validate", help="Validate yml files")
def validate():
    click.secho("Validating config files...")
    validate_all()
    click.secho("All config files are OK", fg="bright_green")


@cli.group("secrets", no_args_is_help=True, help="Manage secrets")
def secrets():
    pass


@secrets.command("add", help="Add one service secret")
@service
@click.argument("key")
@click.argument("value")
def secrets_add(service: str, key: str, value: str):
    Secrets.add(service, key, value)


@secrets.command("add-from-env", help="Add secrets from env file")
@service
@click.argument("env_file_path", type=click.Path(exists=True))
def secrets_add_from_env(service: str, env_file_path: str):
    click.confirm(f"Confirm adding secrets from {env_file_path!r}?", abort=True)
    Secrets.add_from_env(service, env_file_path)


@secrets.command("remove", help="Remove one secret from service")
@service_with_secret
@click.argument("key")
def secrets_remove(service: str, key: str):
    Secrets.remove(service, key)


@secrets.command("list", help="List service secrets")
@service_with_secret
@click.option("-r", "--raw", is_flag=True, help="Show unencrypted secrets")
def secrets_list(service: str, raw):
    Secrets.list(service, raw)


@cli.group("docker", no_args_is_help=True, help="Manage the deployment")
@click.option("--debug", is_flag=True)
@click.option("--ignore-daemon", is_flag=True)
@click.pass_context
def docker(ctx: click.Context, debug: bool, ignore_daemon):
    ctx.ensure_object(dict)
    ctx.obj["debug"] = debug
    ctx.obj["ignore-daemon"] = ignore_daemon


@docker.command("up", help="Create and start service containers")
@services
def docker_up(services: _S):
    DockerCompose.up_d(services)


@docker.command("down", help="Stop and remove all the containers")
@click.option("-v", "--volumes", is_flag=True, help="Remove volumes too")
def docker_down(volumes: bool):
    DockerCompose.down(volumes)


@docker.command("start", help="Start service containers")
@services
def docker_start(services: _S):
    DockerCompose.start(services)


@docker.command("stop", help="Stop service containers")
@services
def docker_stop(services: _S):
    DockerCompose.stop(services)


@docker.command("restart", help="Restart service containers")
@services
def docker_restart(services: _S):
    DockerCompose.restart(services)


@docker.command("ps", help="Show deployment status")
def docker_ps():
    DockerCompose.ps()


@docker.command("logs", help="Show deployment logs")
@services
@click.option("--tail", type=int, help="Show only n lines")
@click.option("-t", "--timestamps", is_flag=True, help="Show timestamps")
@click.option("-f", "--follow", is_flag=True, help="Follow log output")
@click.option("--no-prefix", is_flag=True, help="Don't print prefix in logs")
def docker_logs(
    services: _S, tail: int, follow: bool, timestamps: bool, no_prefix: bool
):
    DockerCompose.logs(
        services=services,
        tail=tail,
        follow=follow,
        timestamps=timestamps,
        no_prefix=no_prefix,
    )


@docker.command("exec", help="Execute a command in a service container")
@service
@click.argument("command")
@click.option("-d", "--detach", is_flag=True, help="Run command in the background")
@click.option(
    "--privileged", is_flag=True, help="Give extended privileges to the process"
)
@click.option("-u", "--user", type=str, help="Run the command as this user")
@click.option("-T", is_flag=True, help="Disable TTY allocation")
@click.option(
    "-e",
    "--env",
    multiple=True,
    type=str,
    callback=check_env,
    help="Set environment variables",
)
@click.option(
    "-w",
    "--workdir",
    metavar="DIR",
    type=str,
    help="Path to workdir directory for this command",
)
def docker_execute(
    service: str,
    command: str,
    detach: bool,
    privileged: bool,
    user: Optional[str],
    t: bool,
    env: List[str],
    workdir: Optional[str],
):
    DockerCompose.exec(
        service=service,
        command=command,
        detach=detach,
        privileged=privileged,
        user=user,
        t=t,
        env=env,
        workdir=workdir,
    )


@docker.command("pull", help="Update the docker image of a container")
@services
def docker_pull(services: _S):
    DockerCompose.pull(services)


@docker.command("dev", help="Update the image, start the service and watch logs")
@service
@click.option("--tail", type=int, help="Show only n lines")
@click.option("-t", "--timestamps", is_flag=True, help="Show timestamps")
def docker_dev(service: str, tail: bool, timestamps: bool):
    DockerCompose.dev(service, tail, timestamps)


@cli.command("paths", help="Show installer paths")
@click.option("-r", "--relative", is_flag=True, help="Show relative paths")
def paths_command(relative: bool):
    paths = (
        ("FENIX_DIR", FENIX_DIR),
        ("INSTALLER_MODULE_DIR", INSTALLER_MODULE_DIR),
        ("INSTALLER_DATA_DIR", INSTALLER_DATA_DIR),
        ("CONFIG_DIR", CONFIG_DIR),
        ("SCHEMAS_DIR", SCHEMAS_DIR),
        ("TEMPLATES_DIR", TEMPLATES_DIR),
    )
    for path_name, path in paths:
        click.secho(path_name + " → ", nl=False, fg="bright_cyan")
        if relative:
            try:
                click.echo(path.relative_to(Path.cwd()).as_posix())
            except ValueError:
                click.secho(path.as_posix(), fg="bright_yellow")
        else:
            click.echo(path.as_posix())

    click.echo()


def main():
    return cli(prog_name="fenix")
