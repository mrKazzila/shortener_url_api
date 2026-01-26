import asyncio

from src.config import server
from src.config.ioc.providers import PROVIDERS
from src.presentation.grpc import GRPC_INTERCEPTORS, GRPC_SERVICES


def new_function():
    pass


def main():
    get_server = server(
        is_reflection_enable=True,
        ioc_providers=PROVIDERS,
        grpc_interceptors=GRPC_INTERCEPTORS,
        grpc_services=GRPC_SERVICES,
    )

    r = new_function()
    print(r)
    asyncio.run(get_server)


if __name__ == "__main__":
    main()
