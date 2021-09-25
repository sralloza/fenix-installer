import os
import platform
import sys

import click
from pathlib import Path

if platform.system() == "Linux":
    DEFAULT_PROFILE = "prod.unsecure.yml"
else:
    DEFAULT_PROFILE = "dev.unsecure.yml"

FENIX_DIR = os.getenv("FENIX_DIR")
if not FENIX_DIR:
    click.secho("ERROR: must set env var FENIX_DIR", fg="bright_red")
    sys.exit(1)

FENIX_DIR = Path(FENIX_DIR)
if not FENIX_DIR.is_dir():
    click.secho(f"ERROR: FENIX_DIR does not exist ({FENIX_DIR})", fg="bright_red")
    sys.exit(1)

if FENIX_DIR.name != "docker":
    click.secho(
        f"WARNING: FENIX_DIR folder name is not docker ({FENIX_DIR})",
        fg="bright_yellow",
    )
    sys.exit(1)

INSTALLER_ROOT_FOLDER = Path(__file__).parent.parent
CONFIG_DIR = INSTALLER_ROOT_FOLDER / "config"
SCHEMAS_DIR = INSTALLER_ROOT_FOLDER / "schemas"
TEMPLATES_DIR = INSTALLER_ROOT_FOLDER / "templates"
MANIFESTS_DIR = FENIX_DIR.parent
