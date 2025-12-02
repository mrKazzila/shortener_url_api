__all__ = ("ErrorMiddleware",)

from time import time
from typing import Any, TypedDict
from urllib import parse

import structlog
from fastapi.responses import JSONResponse
from starlette.datastructures import QueryParams
from starlette.middleware.base import (
    BaseHTTPMiddleware,
    RequestResponseEndpoint,
)
from starlette.requests import Request
from starlette.responses import Response

from src.application.exceptions import BaseApplicationError
from src.domain.exceptions import BaseDomainError
from src.infrastructures.exceptions import BaseInfraError
from src.presentation.exceptions import BasePresentationError

logger = structlog.get_logger(__name__)


class RequestInfo(TypedDict):
    start_time: str
    duration: str
    method: str
    request_path: str
    path_params: dict[str, Any]
    query_params: dict[str, Any]


class ErrorMiddleware(BaseHTTPMiddleware):
    _ERROR_MAP = {
        BaseDomainError: (400, "Domain"),
        BaseApplicationError: (422, "Application"),
        BaseInfraError: (500, "Infrastructure"),
        BasePresentationError: (500, "Presentation"),
        Exception: (500, "Unexpected"),
    }

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        start_time = time()

        try:
            return await call_next(request)

        except tuple(self._ERROR_MAP.keys()) as exc:
            request_info = self._create_request_info_dict(
                request=request,
                start_time=start_time,
            )

            exc_type = next(
                (etype for etype in self._ERROR_MAP if isinstance(exc, etype)),
                Exception,
            )
            status_code, label = self._ERROR_MAP[exc_type]

            logger.error(f"{label}Error [{exc.__class__.__name__}]: {exc}")

            return JSONResponse(
                status_code=status_code,
                content={"error": f"{label}: {exc}", **request_info},
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
