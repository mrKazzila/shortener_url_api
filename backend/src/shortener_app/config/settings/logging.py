__all__ = ("setup_logging",)

import logging
import sys

import structlog


def setup_logging(
    level: str | int = "INFO",
    json_format: bool = False,
) -> None:
    level = _get_log_level(level=level)
    base_processors = _build_default_processors(json_format=json_format)

    _configure_structlog(base_processors=base_processors)
    _configure_default_logging(
        base_processors=base_processors,
        level=level,
        json_format=json_format,
    )
    _tune_noisy_loggers()


def _get_log_level(level: str | int) -> int:
    return (
        getattr(logging, level.upper(), logging.INFO)
        if isinstance(level, str)
        else level
    )


def _configure_structlog(*, base_processors: list) -> None:
    processors = [
        *base_processors,
        structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
    ]

    structlog.configure_once(
        processors=processors,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def _configure_default_logging(
    *,
    base_processors: list,
    json_format: bool,
    level: int,
) -> None:
    renderer = (
        structlog.processors.JSONRenderer()
        if json_format
        else structlog.dev.ConsoleRenderer()
    )

    formatter = structlog.stdlib.ProcessorFormatter(
        foreign_pre_chain=base_processors,
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


def _tune_noisy_loggers() -> None:
    logging.getLogger("aiokafka").setLevel(logging.WARNING)
    logging.getLogger("kafka").setLevel(logging.WARNING)
    logging.getLogger("faststream").setLevel(logging.INFO)


def _build_default_processors(*, json_format: bool) -> list:
    processors = [
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.contextvars.merge_contextvars,
    ]

    if json_format:
        processors.append(
            structlog.processors.CallsiteParameterAdder(
                {
                    structlog.processors.CallsiteParameter.PATHNAME,
                    structlog.processors.CallsiteParameter.FILENAME,
                    structlog.processors.CallsiteParameter.MODULE,
                    structlog.processors.CallsiteParameter.FUNC_NAME,
                    structlog.processors.CallsiteParameter.THREAD,
                    structlog.processors.CallsiteParameter.THREAD_NAME,
                    structlog.processors.CallsiteParameter.PROCESS,
                    structlog.processors.CallsiteParameter.PROCESS_NAME,
                },
            ),
        )
        processors.append(structlog.processors.format_exc_info)

    return processors
