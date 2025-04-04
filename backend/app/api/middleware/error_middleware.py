import logging
from time import time
from typing import Any, TypedDict
from urllib import parse

from fastapi import status
from fastapi.responses import JSONResponse
from starlette.datastructures import QueryParams
from starlette.middleware.base import (
    BaseHTTPMiddleware,
    RequestResponseEndpoint,
)
from starlette.requests import Request
from starlette.responses import Response

__all__ = ("ErrorMiddleware",)

logger = logging.getLogger(__name__)


class RequestInfo(TypedDict):
    start_time: str
    duration: str
    method: str
    request_path: str
    path_params: dict[str, Any]
    query_params: dict[str, Any]


class ErrorMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        start_time = time()

        try:
            return await call_next(request)
        except Exception as exc:
            request_info = self._create_request_info_dict(
                request=request,
                start_time=start_time,
            )
            logger.error(exc)
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "message": (
                        "An unexpected error occurred. "
                        f"Please try again later.\n{exc}"
                    ),
                    "ditail": request_info,
                },
                media_type="application/json",
            )

    def _create_request_info_dict(
        self,
        *,
        request: Request,
        start_time: float,
    ) -> RequestInfo:
        duration = time() - start_time
        q_params = self._get_query_params_to_json(
            params=request.query_params,
        )
        return RequestInfo(
            start_time=f"{start_time}",
            duration=f"{duration:0.3f}",
            method=request.method,
            request_path=f"{request.url.path}",
            path_params=request.path_params,
            query_params=q_params,
        )

    @staticmethod
    def _get_query_params_to_json(*, params: QueryParams) -> dict[str, Any]:
        return dict(parse.parse_qsl(str(params)))
