import logging
import traceback as tb
from typing import Annotated

from fastapi import APIRouter, HTTPException, Path, Request, status
from fastapi.responses import RedirectResponse
from validators import url as url_validator

from app.api.shortener import schemas
from app.api.shortener.services import ShortenerServices as services
from app.core.exceptions import BadRequestException, UrlNotFoundException
from app.service_layer.unit_of_work import UnitOfWork

logger = logging.getLogger(__name__)

router = APIRouter(
    tags=['shortener'],
)


@router.post(
    path='/',
    name='Create key for short url',
    status_code=status.HTTP_201_CREATED,
)
async def create_short_url(
    url: schemas.SUrlBase,
) -> schemas.SUrl:
    """
    Creates a shortened URL.

    Args:
        url: The original URL to shorten.

    Returns:
        The shortened URL information.

    Raises:
        ValueError: If the provided URL is not valid.
    """
    uow = UnitOfWork()
    target_url = str(url.target_url)

    try:
        if url_validator(value=target_url):
            return await services().create_url(
                target_url=target_url,
                uow=uow,
            )

        raise BadRequestException(detail='Your provided URL is not valid!')

    except (BadRequestException, HTTPException) as err:
        trace = tb.format_exception(type(err), err, err.__traceback__)
        logger.error(trace)


@router.get(
    path='/{url_key}',
    name='Redirect to long url by key',
    status_code=status.HTTP_307_TEMPORARY_REDIRECT,
)
async def redirect_to_target_url(
    url_key: Annotated[str, Path(description='The shortened URL key')],
    request: Request,
) -> RedirectResponse:
    """
    Redirects to the target URL for a given shortened URL key.

    Args:
        url_key: The shortened URL key.
        request: The HTTP request object.

    Raises:
        NotFoundError: If the shortened URL key is not found.
    """
    uow = UnitOfWork()

    try:
        if db_url := await services().get_active_long_url_by_key(
            key=url_key,
            uow=uow,
        ):
            await services().update_db_clicks(url=db_url, uow=uow)

            return RedirectResponse(
                url=db_url.target_url,
                status_code=status.HTTP_307_TEMPORARY_REDIRECT,
            )

        url_ = request.url
        raise UrlNotFoundException(detail=f"URL '{url_}' doesn't exist")

    except (UrlNotFoundException, HTTPException) as err:
        trace = tb.format_exception(type(err), err, err.__traceback__)
        logger.error(trace)
