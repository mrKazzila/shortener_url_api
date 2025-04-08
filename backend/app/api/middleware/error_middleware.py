import logging
from http import HTTPStatus
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

from app.exceptions.base import BaseCustomException

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

        except BaseCustomException as exc:
            request_info = self._create_request_info_dict(
                request=request,
                start_time=start_time,
            )
            logger.error(f"{exc.__class__.__name__}: {exc.detail}")

            return JSONResponse(
                status_code=exc.status_code
                if exc.status_code
                else HTTPStatus.INTERNAL_SERVER_ERROR,
                content={
                    "message": exc.__class__.__name__,
                    "details": exc.detail,
                    "request_info": request_info,
                },
            )

        except Exception as exc:
            request_info = self._create_request_info_dict(
                request=request,
                start_time=start_time,
            )
            logger.exception("Unhandled exception occurred")

            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "message": f"{exc.__class__.__name__}",
                    "details": "Unhandled exception occurred",
                    "request_info": request_info,
                },
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
