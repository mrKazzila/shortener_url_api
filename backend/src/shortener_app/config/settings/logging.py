from __future__ import annotations

__all__ = (
    "LoggingConfig",
    "LogRenderer",
    "LOG_RENDERERS",
    "NOISY_LOGGERS",
    "setup_logging",
    "reset_logging",
)

import logging
import sys
from dataclasses import dataclass
from typing import Final, Literal, cast

import structlog
from structlog.processors import CallsiteParameter
from structlog.typing import BindableLogger, Processor

type LogRenderer = Literal["console", "json"]

LOG_RENDERERS: Final[tuple[LogRenderer, ...]] = ("console", "json")

NOISY_LOGGERS: Final[dict[str, int]] = {
    "aiokafka": logging.WARNING,
    "kafka": logging.WARNING,
    "faststream": logging.INFO,
}


@dataclass(frozen=True, slots=True, kw_only=True)
class LoggingConfig:
    level: str | int = "INFO"
    renderer: LogRenderer = "console"
    enable_diagnostics: bool = False
    use_utc_timestamps: bool = False

    def resolved_level(self) -> int:
        return _get_log_level(self.level)


def setup_logging(config: LoggingConfig | None = None) -> None:
    cfg = config or LoggingConfig()
    level = cfg.resolved_level()

    shared_processors = _build_shared_processors(
        use_utc=cfg.use_utc_timestamps,
    )
    foreign_processors = _build_foreign_processors(
        use_utc=cfg.use_utc_timestamps,
    )
    diagnostic_processors = _build_diagnostic_processors(
        enable_diagnostics=cfg.enable_diagnostics,
    )
    exception_processors = _build_exception_processors(renderer=cfg.renderer)
    renderer_processor = _build_renderer(renderer=cfg.renderer)

    _configure_structlog(
        level=level,
        shared_processors=shared_processors,
        diagnostic_processors=diagnostic_processors,
        exception_processors=exception_processors,
    )
    _configure_stdlib_logging(
        level=level,
        foreign_processors=foreign_processors,
        renderer=renderer_processor,
    )
    _tune_noisy_loggers()


def reset_logging() -> None:
    structlog.reset_defaults()


def _get_log_level(level: str | int) -> int:
    if isinstance(level, int):
        return level

    normalized = logging.getLevelName(level.upper())
    return normalized if isinstance(normalized, int) else logging.INFO


def _configure_structlog(
    *,
    level: int,
    shared_processors: list[Processor],
    diagnostic_processors: list[Processor],
    exception_processors: list[Processor],
) -> None:
    processors: list[Processor] = [
        *shared_processors,
        structlog.stdlib.PositionalArgumentsFormatter(),
        *diagnostic_processors,
        structlog.processors.StackInfoRenderer(),
        *exception_processors,
        structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
    ]

    structlog.configure(
        processors=processors,
        wrapper_class=cast(
            type[BindableLogger],
            cast(object, structlog.stdlib.BoundLogger),
        ),
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    logging.getLogger().setLevel(level)


def _configure_stdlib_logging(
    *,
    level: int,
    foreign_processors: list[Processor],
    renderer: Processor,
) -> None:
    formatter = structlog.stdlib.ProcessorFormatter(
        foreign_pre_chain=[
            *foreign_processors,
            structlog.stdlib.PositionalArgumentsFormatter(),
        ],
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            renderer,
        ],
    )

    handler = logging.StreamHandler(stream=sys.stdout)
    handler.setFormatter(formatter)

    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(level)


def _build_shared_processors(*, use_utc: bool) -> list[Processor]:
    return [
        structlog.stdlib.filter_by_level,
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso", utc=use_utc),
    ]


def _build_foreign_processors(*, use_utc: bool) -> list[Processor]:
    return [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso", utc=use_utc),
    ]


def _build_diagnostic_processors(
    *,
    enable_diagnostics: bool,
) -> list[Processor]:
    if not enable_diagnostics:
        return []

    return [
        structlog.processors.CallsiteParameterAdder(
            {
                CallsiteParameter.MODULE,
                CallsiteParameter.FUNC_NAME,
                CallsiteParameter.LINENO,
            },
        ),
    ]


def _build_exception_processors(*, renderer: LogRenderer) -> list[Processor]:
    if renderer == "json":
        return [
            structlog.processors.dict_tracebacks,
        ]

    return []


def _build_renderer(*, renderer: LogRenderer) -> Processor:
    if renderer == "json":
        return structlog.processors.JSONRenderer()

    return structlog.dev.ConsoleRenderer()


def _tune_noisy_loggers() -> None:
    for logger_name, level in NOISY_LOGGERS.items():
        logging.getLogger(logger_name).setLevel(level)
