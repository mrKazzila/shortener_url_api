__all__ = ("setup_logging",)

import logging
import sys

import structlog


def setup_logging(
    level: str | int = "INFO",
    json_format: bool = False,
) -> None:
    if isinstance(level, str):
        level = getattr(logging, level.upper(), logging.INFO)

    _configure_structlog(json_format=json_format)
    _configure_default_logging(level=level, json_format=json_format)


def _build_default_processors(json_format: bool):
    processors = [
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.contextvars.merge_contextvars,
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
    ]

    if json_format:
        processors.append(structlog.processors.format_exc_info)

    return processors


def _configure_structlog(json_format: bool):
    structlog.configure_once(
        processors=_build_default_processors(json_format=json_format)
        + [
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
    )


def _configure_default_logging(*, level: int, json_format: bool):
    renderer = (
        structlog.processors.JSONRenderer()
        if json_format
        else structlog.dev.ConsoleRenderer()
    )

    formatter = structlog.stdlib.ProcessorFormatter(
        processors=_build_default_processors(json_format=json_format)
        + [
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
