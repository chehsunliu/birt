import logging
import sys

import structlog
from structlog.stdlib import ProcessorFormatter
from structlog.types import Processor

shared_processors: list[Processor] = [
    structlog.contextvars.merge_contextvars,
    structlog.processors.add_log_level,
    structlog.processors.StackInfoRenderer(),
    structlog.dev.set_exc_info,
    structlog.processors.format_exc_info,
    structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S.%fZ", utc=True),
    structlog.processors.CallsiteParameterAdder(
        [
            structlog.processors.CallsiteParameter.FILENAME,
            structlog.processors.CallsiteParameter.LINENO,
        ]
    ),
]


def configure_logger(log_level: int):
    _configure_structlog(log_level)
    _configure_logging(log_level)


def _configure_structlog(log_level: int):
    processors: list[Processor] = [*shared_processors, structlog.processors.JSONRenderer(separators=(",", ":"))]

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(log_level),
    )


def _configure_logging(log_level: int):
    processors: list[Processor] = [
        ProcessorFormatter.remove_processors_meta,
        structlog.processors.JSONRenderer(separators=(",", ":")),
    ]

    formatter = ProcessorFormatter(
        foreign_pre_chain=shared_processors,
        processors=processors,
    )

    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(formatter)
    logging.basicConfig(handlers=[handler], level=logging.INFO)

    logger = logging.getLogger("uvicorn.error")
    logger.handlers = [handler]
    logger.propagate = False
