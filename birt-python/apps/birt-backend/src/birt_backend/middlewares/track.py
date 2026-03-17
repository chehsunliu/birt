import math
import time
import uuid
from typing import Any

import structlog
from starlette.requests import Request
from starlette.types import ASGIApp, Message, Receive, Scope, Send

logger = structlog.getLogger(__name__)


class RequestIdMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        logger.debug("Apply RequestIdMiddleware")
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request = Request(scope, receive, send)
        x_request_id = request.headers.get("X-Birt-Request-Id")
        x_request_id_has_been_set = True
        if not x_request_id:
            x_request_id_has_been_set = False
            x_request_id = str(uuid.uuid4())

        with structlog.contextvars.bound_contextvars(x_request_id=x_request_id):
            if not x_request_id_has_been_set:
                logger.warning("x-request-id is not set")
            await self.app(scope, receive, send)


class AccessLoggerMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        logger.debug("Apply AccessLoggerMiddleware")
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        t0 = time.time()
        request = Request(scope, receive, send)

        # Headers from Nginx/OAuth2-Proxy:
        # {
        #   "x-user": "631eb114-6470-4912-9bed-e109fcedf88f",
        #   "x-access-token": "eyJhbGciOiJS...",
        #   "authorization": "Bearer eyJhbGciOiJSUzI1NiIsI...",
        #   "host": "localhost:8080",
        #   "connection": "close",
        #   "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:145.0) Gecko/20100101 Firefox/145.0",
        #   "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        #   "accept-encoding": "gzip, br",
        #   "accept-language": "en-US,en;q=0.5",
        #   "alt-used": "dlh-stg.chliuazw.app",
        #   "cdn-loop": "cloudflare; loops=1",
        #   "cf-connecting-ip": "114.37.207.191",
        #   "cf-ipcountry": "TW",
        #   "cf-ray": "9a9e45998d5acce4-SJC",
        #   "cf-visitor": "{\"scheme\":\"https\"}",
        #   "cf-warp-tag-id": "57caf18b-9ed1-4d8a-8edb-19d824a106ef",
        #   "cookie": "_oauth2_proxy=NkmP5q...|1765050202|7xZASJOKXdx...",
        #   "priority": "u=0, i",
        #   "sec-fetch-dest": "document",
        #   "sec-fetch-mode": "navigate",
        #   "sec-fetch-site": "none",
        #   "sec-fetch-user": "?1",
        #   "upgrade-insecure-requests": "1",
        #   "x-forwarded-for": "114.37.207.191,10.1.143.220",
        #   "x-forwarded-proto": "http",
        #   "x-envoy-external-address": "10.1.143.220",
        #   "x-request-id": "7463106f-5116-49ce-826f-050a2635a59e",
        #   "x-envoy-attempt-count": "1",
        #   "x-forwarded-client-cert": "By=spiffe://cluster.local/ns/dlh/sa/default;Hash=4948153d1...;Subject=\"\";URI=spiffe://cluster.local/ns/istio-ingress/sa/istio-ingress-stg"
        # }

        header_names = [
            "User-Agent",
            "X-Birt-Request-Id",
        ]
        headers = {k: request.headers[k] for k in header_names if k in request.headers}

        info: dict[str, Any] = {
            "method": request.method,
            "path": request.url.path,
            "query_params": str(request.url.query) if request.url.query else None,
            "headers": headers,
        }

        async def send_wrapper(message: Message) -> None:
            if message["type"] == "http.response.start":
                info["status_code"] = message["status"]
            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
            logger.info("access-log", response_time_ms=_get_response_time_ms(t0), **info)
        except Exception as e:
            logger.info("access-log", response_time_ms=_get_response_time_ms(t0), status_code=500, **info)
            raise e


def _get_response_time_ms(t0: float) -> int:
    response_time_ms = math.ceil((time.time() - t0) * 1000)
    return int(response_time_ms)
