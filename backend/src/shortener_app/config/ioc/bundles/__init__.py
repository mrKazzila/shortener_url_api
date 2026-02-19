__all__ = (
    "GRPC_PROVIDERS",
    "CONSUMER_PROVIDERS",
)

from shortener_app.config.ioc.bundles.common import (
    COMMON_PROVIDERS as _COMMON_PROVIDERS,
)
from shortener_app.config.ioc.bundles.consumer import (
    CONSUMER_ONLY_PROVIDERS as _CONSUMER_ONLY_PROVIDERS,
)
from shortener_app.config.ioc.bundles.grpc import (
    GRPC_ONLY_PROVIDERS as _GRPC_ONLY_PROVIDERS,
)

GRPC_PROVIDERS = (
    *_COMMON_PROVIDERS,
    *_GRPC_ONLY_PROVIDERS,
)

CONSUMER_PROVIDERS = (
    *_COMMON_PROVIDERS,
    *_CONSUMER_ONLY_PROVIDERS,
)
