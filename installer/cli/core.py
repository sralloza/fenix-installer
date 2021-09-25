import shlex
from pathlib import Path
from typing import List, Optional

import click

from ..aws import get_secrets, set_secrets
from .exceptions import SecretNotFound
from .process import run_docker_compose_command
from .utils import get_service_by_name

_S = List[str]


class Secrets:
    @staticmethod
    def add(service_name: str, key: str, value: str):
        service = get_service_by_name(service_name)
        secrets = get_secrets(service)
        secrets.append(f"{key}={value}")
        set_secrets(service, secrets)

    @staticmethod
    def add_from_env(service_name: str, env_file_path: str):
        service = get_service_by_name(service_name)
        env_secrets = Path(env_file_path).read_text("utf8").splitlines()
        secrets = get_secrets(service)
        secrets.extend(env_secrets)
        set_secrets(service, secrets)

    @staticmethod
    def remove(service_name: str, key: str):
        service = get_service_by_name(service_name)
        secrets = get_secrets(service)
        for secret in secrets:
            secret_key, _ = secret.split("=", 1)
            if secret_key == key:
                secrets.remove(secret)
                return set_secrets(service, secrets)
        raise SecretNotFound(service, key)

    @staticmethod
    def list(service_name: str, raw: bool):
        service = get_service_by_name(service_name)
        secrets = get_secrets(service)
        for secret in secrets:
            key, value = secret.split("=", 1)
            msg = f"{key}="
            if raw:
                msg += value
            else:
                msg += "*" * 8
            click.echo(msg)


class DockerCompose:
    @staticmethod
    def up_d(services: _S):
        args = ["up", "-d"]
        if services:
            args.append(shlex.join(services))

        return run_docker_compose_command(args)

    @staticmethod
    def down(volumes: bool):
        args = ["down"]
        if volumes:
            args.append("-v")
        return run_docker_compose_command(args)

    @staticmethod
    def start(services: _S):
        args = ["start"]
        if services:
            args.append(shlex.join(services))

        return run_docker_compose_command(args)

    @staticmethod
    def stop(services: _S):
        args = ["stop"]
        if services:
            args.append(shlex.join(services))

        return run_docker_compose_command(args)

    @staticmethod
    def restart(services: _S):
        args = ["restart"]
        if services:
            args.append(shlex.join(services))

        return run_docker_compose_command(args)

    @staticmethod
    def ps():
        return run_docker_compose_command(["ps"])

    @staticmethod
    def logs(
        services: _S,
        tail: int = None,
        follow: bool = False,
        timestamps: bool = False,
        no_prefix: bool = False,
    ):
        args = ["logs"]
        if follow:
            args.append("-f")
        if timestamps:
            args.append("-t")
        if no_prefix:
            args.append("--no-log-prefix")
        if no_prefix:
            args.extend(["-t", str(tail)])
        if services:
            args.append(shlex.join(services))

        return run_docker_compose_command(args)

    @staticmethod
    def exec(
        service: str,
        command: str,
        detach: bool,
        privileged: bool,
        user: Optional[str],
        t: bool,
        env: List[str],
        workdir: Optional[str],
    ):
        args = ["exec"]
        if detach:
            args.append("-d")
        if privileged:
            args.append("--privileged")
        if user:
            args.extend(["-u", user])
        if t:
            args.append("-T")
        if env:
            for var in env:
                args.extend(["--env", var])
        if workdir:
            args.extend(["-w", workdir])

        args.extend([service, shlex.quote(command)])
        return run_docker_compose_command(args)

    @staticmethod
    def pull(services: _S):
        args = ["pull"]
        if services:
            args.append(shlex.join(services))

        return run_docker_compose_command(args)

    @classmethod
    def dev(cls, service: str, tail: int = None, timestamps: bool = False):
        cls.pull([service])
        cls.up_d([service])
        cls.logs([service], follow=True, tail=tail, timestamps=timestamps)
