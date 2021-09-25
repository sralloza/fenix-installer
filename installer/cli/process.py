from installer.cli.exceptions import DockerNotRunningError
import logging
import subprocess
from typing import Dict, List

import click

from ..architecture import FENIX_DIR
from ..context import profile_context
from ..controller import get_default_profile
from .utils import shlex_join

logger = logging.getLogger(__name__)
logging.basicConfig()


def is_docker_running():
    try:
        subprocess.check_output(["docker", "info"], stderr=False)
        return True
    except subprocess.CalledProcessError:
        return False


def run_docker_compose_command(args: List[str]):
    if not is_docker_running():
        raise DockerNotRunningError()

    debug = click.get_current_context().obj["debug"]
    profile = get_default_profile()
    with profile_context(profile, debug) as profile_path:
        args = ["docker-compose", "-f", profile_path.as_posix()] + args
        run_command(args)


def run_command(args: List[str], timeout=30, env: Dict[str, str] = None):
    command_to_log = shlex_join(args)
    logger.info(f"Running command: {command_to_log}")
    print(f"Running command: {command_to_log!r}")

    with subprocess.Popen(
        args,
        # stdout=subprocess.PIPE,
        # stderr=subprocess.PIPE,
        cwd=FENIX_DIR,
        env=env,
        text=True,
        start_new_session=True,
    ) as process:
        try:
            stdout, stderr = process.communicate(timeout=timeout)
        except subprocess.TimeoutExpired:
            logger.debug(f"Command timed out after {timeout} seconds.")
            process.kill()
            stdout, stderr = process.communicate()
            raise subprocess.TimeoutExpired(
                process.args, timeout, output=stdout, stderr=stderr
            ) from None
        except:  # Including KeyboardInterrupt, communicate handled that
            try:
                process.kill()
            except ProcessLookupError:
                # The process no longer exists, probably it terminated before reaching this point
                pass
            # We don't call process.wait() as .__exit__ does that for us
            raise

        returncode = process.poll()

    return returncode
