from copy import deepcopy
from typing import Dict, List, Optional

import attr

from ..attrs_utils.converters import builder, default_list
from ..attrs_utils.validators import validate_required_services
from ..models import OptionalProdDevStr


@attr.s(auto_attribs=True)
class Service:
    # Required settings
    name: str
    image: OptionalProdDevStr = attr.ib(converter=builder)
    url: OptionalProdDevStr = attr.ib(converter=builder)

    # Special settings
    auth: Optional[str]
    enabled: bool = attr.ib(validator=validate_required_services)
    secrets: bool
    service_name: Optional[str]
    traefik_port: Optional[int]

    # Docker settings
    commands_https: List[str] = attr.ib(converter=default_list)
    commands: List[str] = attr.ib(converter=default_list)
    _environment: Dict[str, str]
    port_map: List[int] = attr.ib(converter=default_list)
    volumes: List[str] = attr.ib(converter=default_list)

    # Other settings
    disable_restart: bool
    path_prefix: Optional[str]

    @property
    def environment(self):
        if isinstance(self._environment, dict):
            environ = deepcopy(self._environment)
        else:
            environ = {}
        environ["TZ"] = "Europe/Madrid"
        return environ

    @property
    def default(self):
        return self.name == "default"
