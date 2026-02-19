import asyncio

from shortener_app.config import server
from shortener_app.config.ioc.providers import get_providers
from shortener_app.config.settings.logging import setup_logging
from shortener_app.presentation.grpc import GRPC_INTERCEPTORS, GRPC_SERVICES


def main() -> None:
    get_server = server(
        is_reflection_enable=True,
        ioc_providers=get_providers(is_consumer=False),
        grpc_interceptors=GRPC_INTERCEPTORS,
        grpc_services=GRPC_SERVICES,
    )

    asyncio.run(get_server)


if __name__ == "__main__":
    setup_logging(
        json_format=False,
        level="INFO",
    )
    main()
