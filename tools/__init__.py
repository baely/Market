from decimal import Decimal
from enum import Enum

from typing import Any, List, Union


def mean(items: List[Union[int, float, Decimal]]):
    return sum(items) / len(items)


def to_dict(obj: Any) -> Union[dict, list, int, float, str, bool, None]:
    if isinstance(obj, (dict, list, int, float, str, bool)) or obj is None:
        return obj
    if isinstance(obj, Enum):
        return obj.name
    if isinstance(obj, Decimal):
        return float(str(obj))
    return {
        key: to_dict(val) for key, val in obj.__dict__.items()
    }
