from dataclasses import dataclass, field
from typing import Any


@dataclass
class FakeCache:
    """
    In-memory fake cache + spy on calls.
    """

    store: dict[str, Any] = field(default_factory=dict)

    get_calls: list[str] = field(default_factory=list)
    set_calls: list[tuple[str, dict[str, Any], int | None]] = field(
        default_factory=list,
    )
    delete_calls: list[str] = field(default_factory=list)
    exists_calls: list[str] = field(default_factory=list)
    clear_calls: list[str] = field(default_factory=list)
    set_nx_calls: list[tuple[str, dict[str, Any] | str, int | None]] = field(
        default_factory=list,
    )
    set_nx_results: list[bool] = field(default_factory=list)

    set_result: bool = True
    raise_on_set: Exception | None = None

    async def get(self, key: str) -> dict[str, Any] | None:
        self.get_calls.append(key)
        val = self.store.get(key)
        return val if isinstance(val, dict) else None

    async def set(
        self,
        key: str,
        value: dict[str, Any],
        ttl: int | None = None,
    ) -> bool:
        self.set_calls.append((key, value, ttl))

        if self.raise_on_set is not None:
            raise self.raise_on_set

        if self.set_result:
            self.store[key] = value

        return self.set_result

    async def delete(self, key: str) -> bool:
        self.delete_calls.append(key)
        return self.store.pop(key, None) is not None

    async def exists(self, key: str) -> bool:
        self.exists_calls.append(key)
        return key in self.store

    async def clear(self, pattern: str) -> int:
        self.clear_calls.append(pattern)
        n = len(self.store)
        self.store.clear()
        return n

    async def set_nx(
        self,
        key: str,
        value: dict[str, Any] | str,
        ttl_seconds: int | None = None,
    ) -> bool:
        self.set_nx_calls.append((key, value, ttl_seconds))

        if key in self.store:
            return False

        if self.set_nx_results:
            res = (
                self.set_nx_results.pop(0)
                if len(self.set_nx_results) > 1
                else self.set_nx_results[0]
            )
        else:
            res = True

        if not res:
            return False

        self.store[key] = value
        return True
