import re
from typing import Annotated

from fastapi import Path, Query

__all__ = (
    "PathUrlKey",
    "QueryLongUrl",
)

_URL_REGEX = re.compile(
    r"^https?://[^\s/$.?#].[^\s]*$",
    re.IGNORECASE,
)

QueryLongUrl = Annotated[
    str,
    Query(
        description="Initial long URL for shortening",
        example="https://www.youtube.com/",
        regex=_URL_REGEX.pattern,
    ),
]

PathUrlKey = Annotated[
    str,
    Path(
        description="The shortened URL key",
        min_length=5,
        max_length=5,
        example="Rlu9d",
    ),
]
