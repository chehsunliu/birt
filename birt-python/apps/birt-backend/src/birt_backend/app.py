import logging

import structlog
from fastapi import FastAPI

from birt_backend.features.health.routes import router as health_router
from birt_backend.instances import default_settings
from birt_backend.logging import configure_logger
from birt_backend.middlewares import JsonResponseMiddleware
from birt_backend.middlewares.track import AccessLoggerMiddleware, RequestIdMiddleware

logger = structlog.get_logger(__name__)
configure_logger(log_level=logging.getLevelName(default_settings.log_level))

app = FastAPI()
app.include_router(health_router)

app.add_middleware(JsonResponseMiddleware)
app.add_middleware(AccessLoggerMiddleware)
app.add_middleware(RequestIdMiddleware)
