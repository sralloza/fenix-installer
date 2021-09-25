from typing import Optional

import attr


@attr.s(auto_attribs=True)
class Profile:
    name: str
    prod: bool
    https: bool
    traefik_token: Optional[str]
    enabled: bool
