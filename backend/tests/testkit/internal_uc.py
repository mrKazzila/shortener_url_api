from dataclasses import dataclass, field

from shortener_app.application.dtos.urls.urls_cache import UrlCacheSeedDTO


@dataclass
class FakeCreateUniqKeyUseCase:
    return_key: str = "Ab12Z"
    calls: list[UrlCacheSeedDTO] = field(default_factory=list)
    exc: Exception | None = None

    async def execute(self, *, seed: UrlCacheSeedDTO) -> str:
        self.calls.append(seed)
        if self.exc is not None:
            raise self.exc
        return self.return_key
