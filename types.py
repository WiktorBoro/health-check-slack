# types.py
from typing import TypedDict, List


class ToChecksTypedDict(TypedDict):
    url_base: str
    params: List[str]
