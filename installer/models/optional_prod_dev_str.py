from typing import Optional

import attr


@attr.s(auto_attribs=True)
class OptionalProdDevStr:
    prod: Optional[str]
    dev: Optional[str]
