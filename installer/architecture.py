import os
import platform
import sys
from pathlib import Path

import click

if platform.system() == "Linux":
    DEFAULT_PROFILE = "prod.unsecure"
else:
    DEFAULT_PROFILE = "dev.unsecure"

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

if not os.getenv("AWS_ACCESS_KEY_ID"):
    click.secho("ERROR: must set env var AWS_ACCESS_KEY_ID", fg="bright_red")
    sys.exit(1)

if not os.getenv("AWS_SECRET_ACCESS_KEY"):
    click.secho("ERROR: must set env var AWS_SECRET_ACCESS_KEY", fg="bright_red")
    sys.exit(1)

INSTALLER_MODULE_DIR = Path(__file__).parent
INSTALLER_DATA_DIR = INSTALLER_MODULE_DIR / "data"
CONFIG_DIR = INSTALLER_DATA_DIR / "config"
SCHEMAS_DIR = INSTALLER_DATA_DIR / "schemas"
TEMPLATES_DIR = INSTALLER_DATA_DIR / "templates"
# MANIFESTS_DIR = FENIX_DIR.parent
