import asyncio

from shortener_app.config.ioc.consumer_providers import get_consumer_providers
from shortener_app.config.settings.logging import LoggingConfig, setup_logging
from shortener_app.infrastructures.broker.consumers.common import (
    init_container,
)
from shortener_app.infrastructures.broker.consumers.consumer_new_url import (
    run_subscriber,
)


async def main():
    providers = get_consumer_providers()
    container = await init_container(providers=providers)
    await run_subscriber(container=container)


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
