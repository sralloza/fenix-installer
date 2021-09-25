from typing import Dict

from ..models import OptionalProdDevStr


def builder(value: Dict[str, str]):
    return OptionalProdDevStr(**value)


def default_list(value):
    if value:
        return value
    return []
