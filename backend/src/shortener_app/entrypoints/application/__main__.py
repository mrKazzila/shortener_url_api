import asyncio

from shortener_app.config.ioc.grpc_providers import get_grpc_providers
from shortener_app.config.settings.logging import LoggingConfig, setup_logging
from shortener_app.config.setup import server
from shortener_app.presentation.grpc import GRPC_INTERCEPTORS, GRPC_SERVICES


async def main() -> None:
    get_server = server(
        is_reflection_enable=True,
        ioc_providers=get_grpc_providers(),
        grpc_interceptors=GRPC_INTERCEPTORS,
        grpc_services=GRPC_SERVICES,
    )

    await get_server

    # asyncio.run(get_server)


if __name__ == "__main__":
    setup_logging(
        config=LoggingConfig(
            level="INFO",
            renderer="console",
            enable_diagnostics=False,
            use_utc_timestamps=True,
        ),
    )

    asyncio.run(main())
