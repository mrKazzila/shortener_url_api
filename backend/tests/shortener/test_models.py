import pytest
from backend.app.shortener.models import Url
from sqlalchemy import select
from sqlalchemy.exc import DBAPIError, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.selectable import Select

from backend.tests.conftest import async_session_maker


def select_by(model_params, value: str) -> Select:
    query = (
        select(Url)
        .filter(model_params == value)
    )
    return query


async def test_create_url(async_session: AsyncSession) -> None:
    """
    Test that a URL can be created.

    Args:
         async_session (AsyncSession): The database session.
    """
    url = Url(
        key='foo',
        secret_key='bar',
        target_url='https://www.google.com',
    )

    async_session.add(url)
    await async_session.commit()

    assert url in async_session
    assert url.key == 'foo'
    assert url.secret_key == 'bar'
    assert url.target_url == 'https://www.google.com'
    assert url.is_active is True
    assert url.clicks_count == 0


async def test_get_url_by_key(async_session: AsyncSession) -> None:
    """
    Test that a URL can be retrieved by its key.

    Args:
         async_session (AsyncSession): The database session.
    """
    url = Url(
        key='foq',
        secret_key='baq',
        target_url='https://www.google.com',
    )
    async_session.add(url)
    await async_session.commit()

    query = select_by(model_params=Url.key, value='foq')
    result = await async_session.execute(query)
    row = result.scalar()

    assert url == row


async def test_get_url_by_secret_key(async_session: AsyncSession) -> None:
    """
    Tests that a URL can be retrieved by its secret key.

    Args:
         async_session (AsyncSession): The database session.
    """
    url = Url(
        key='fod',
        secret_key='bas',
        target_url='https://www.google.com',
    )

    async_session.add(url)
    await async_session.commit()

    query = select_by(model_params=Url.secret_key, value='bas')
    result = await async_session.execute(query)
    row = result.scalar()

    assert url == row


async def test_update_url(async_session: AsyncSession) -> None:
    """
    Tests that a URL can be updated.

    Args:
         async_session (AsyncSession): The database session.
    """
    url = Url(
        key='fop',
        secret_key='bir',
        target_url='https://www.google.com',
    )

    async_session.add(url)
    await async_session.commit()

    url.target_url = 'https://www.zoom.com'
    await async_session.commit()

    query = select_by(model_params=Url.key, value='fop')
    result = await async_session.execute(query)
    row = result.scalar()

    assert row.target_url == 'https://www.zoom.com'


async def test_delete_url(async_session: AsyncSession) -> None:
    """
    Tests that a URL can be deleted.

    Args:
         async_session (AsyncSession): The database session.
    """
    url = Url(
        key='fbo',
        secret_key='bcr',
        target_url='https://www.google.com',
    )

    async_session.add(url)
    await async_session.commit()

    await async_session.delete(url)
    await async_session.commit()

    assert url not in async_session


async def test_create_url_with_invalid_key(async_session: AsyncSession) -> None:
    """
    Tests that a URL cannot be created with an invalid key.

    Args:
         async_session (AsyncSession): The database session.
    """
    with pytest.raises(DBAPIError):
        url = Url(
            key=12345,
            secret_key='bhr',
            target_url='https://www.google.com',
        )
        async_session.add(url)
        await async_session.commit()


async def test_create_url_with_duplicate_key() -> None:
    """Tests that a URL cannot be created with a duplicate key."""
    async with async_session_maker() as session:
        url1 = Url(
            key='fyn',
            secret_key='aar',
            target_url='https://www.google.com',
        )
        session.add(url1)
        await session.commit()

        with pytest.raises(IntegrityError):
            url2 = Url(
                key='fyn',
                secret_key='aar',
                target_url='https://www.facebook.com',
            )
            session.add(url2)
            await session.commit()