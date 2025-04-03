from typing import Annotated

from fastapi import Path, Query
from pydantic import HttpUrl

__all__ = (
    "PathUrlKey",
    "QueryLongUrl",
)

QueryLongUrl = Annotated[
    HttpUrl,
    Query(description="Initial long URL for shortening"),
]
PathUrlKey = Annotated[str, Path(description="The shortened URL key")]
