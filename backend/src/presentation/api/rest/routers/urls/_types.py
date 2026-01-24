__all__ = (
    "PathUrlKey",
    "QueryLongUrl",
    "QueryUrlName",
    "QueryUrlIsActive",
)

import re
from typing import Annotated

from fastapi import Path, Query

_URL_REGEX = re.compile(
    r"^https?://[^\s/$.?#].[^\s]*$",
    re.IGNORECASE,
)

QueryLongUrl = Annotated[
    str,
    Query(
        description="The original URL",
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
        example="LiNks",
    ),
]

QueryUrlName = Annotated[
    str | None,
    Query(
        ...,
        description="The URL title/name",
        max_length=300,
    ),
]

QueryUrlIsActive = Annotated[
    bool | None,
    Query(
        ...,
        description="Whether the URL is active or not",
    ),
]
