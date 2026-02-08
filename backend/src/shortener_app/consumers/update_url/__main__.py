import asyncio

from shortener_app.config.settings.logging import setup_logging
from shortener_app.infrastructures.broker.consumers.consumer_update_url import main

if __name__ == "__main__":
    setup_logging(
        json_format=False,
        level="INFO",
    )
    asyncio.run(main())
