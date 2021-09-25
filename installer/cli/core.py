import shlex
from typing import List, Optional

from ..architecture import DEFAULT_PROFILE
from .process import run_command

BASE_COMMAND = ["docker-compose", "-f", DEFAULT_PROFILE]
_S = List[str]


class DockerCompose:
    @staticmethod
    def up_d(services: _S):
        args = BASE_COMMAND + ["up", "-d"]
        if services:
            args.append(shlex.join(services))

        return run_command(args)

    @staticmethod
    def down(volumes: bool):
        args = BASE_COMMAND + ["down"]
        if volumes:
            args.append("-v")
        return run_command(args)

    @staticmethod
    def start(services: _S):
        args = BASE_COMMAND + ["start"]
        if services:
            args.append(shlex.join(services))

        return run_command(args)

    @staticmethod
    def stop(services: _S):
        args = BASE_COMMAND + ["stop"]
        if services:
            args.append(shlex.join(services))

        return run_command(args)

    @staticmethod
    def restart(services: _S):
        args = BASE_COMMAND + ["restart"]
        if services:
            args.append(shlex.join(services))

        return run_command(args)

    @staticmethod
    def ps():
        return run_command(BASE_COMMAND + ["ps"])

    @staticmethod
    def logs(
        services: _S,
        tail: int = None,
        follow: bool = False,
        timestamps: bool = False,
        no_prefix: bool = False,
    ):
        args = BASE_COMMAND + ["logs"]
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

        return run_command(args)

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
        args = BASE_COMMAND + ["exec"]
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
        return run_command(args)

    @staticmethod
    def pull(services: _S):
        args = BASE_COMMAND + ["pull"]
        if services:
            args.append(shlex.join(services))

        return run_command(args)

    @classmethod
    def dev(cls, service: str, tail: int = None, timestamps: bool = False):
        cls.pull([service])
        cls.up_d([service])
        cls.logs([service], follow=True, tail=tail, timestamps=timestamps)
