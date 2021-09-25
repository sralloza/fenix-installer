import logging
import subprocess
from typing import Dict, List

from ..architecture import MANIFESTS_DIR
from .utils import shlex_join

logger = logging.getLogger(__name__)
logging.basicConfig()


def run_command(args: List[str], timeout=30, env: Dict[str, str] = None):
    command_to_log = shlex_join(args)
    logger.info(f"Running command: {command_to_log}")
    print(f"Running command: {command_to_log}")

    with subprocess.Popen(
        args,
        # stdout=subprocess.PIPE,
        # stderr=subprocess.PIPE,
        cwd=MANIFESTS_DIR,
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
