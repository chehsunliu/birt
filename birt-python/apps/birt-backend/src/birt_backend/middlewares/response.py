import json

from starlette.types import ASGIApp, Message, Receive, Scope, Send


class JsonResponseMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        status_code: int | None = None
        headers = []
        body_chunks: list[bytes] = []
        content_type = None
        pass_through = False

        async def send_wrapper(message: Message) -> None:
            nonlocal status_code, headers, body_chunks, content_type, pass_through

            if message["type"] == "http.response.start":
                status_code = message["status"]
                headers = list(message.get("headers", []))
                # Extract content-type from headers
                for name, value in headers:
                    if name.lower() == b"content-type":
                        content_type = value.decode("utf-8", errors="ignore")
                        break

                # Pass through 204 No Content immediately
                if status_code == 204:
                    pass_through = True
                    await send(message)
                    return

            elif message["type"] == "http.response.body":
                if pass_through:
                    # Pass through 204 responses as-is
                    await send(message)
                    return

                if message.get("body"):
                    body_chunks.append(message["body"])
                if not message.get("more_body", False):
                    # All body chunks received, process the response
                    await process_response()
                # Don't forward body messages yet - we'll send processed version

        async def process_response() -> None:
            if not content_type or "application/json" not in content_type:
                # Not JSON, send original response
                await send(
                    {
                        "type": "http.response.start",
                        "status": status_code,
                        "headers": headers,
                    }
                )
                for chunk in body_chunks:
                    await send({"type": "http.response.body", "body": chunk})
                await send({"type": "http.response.body", "body": b""})
                return

            # Combine all body chunks
            body = b"".join(body_chunks)

            try:
                original_data = json.loads(body)

                # Wrap the response data
                if status_code and status_code >= 400:
                    wrapped_data = {"error": original_data}
                else:
                    wrapped_data = {"data": original_data}

                new_body = json.dumps(wrapped_data).encode("utf-8")

                # Update headers: remove content-length, ensure content-type
                new_headers = [(name, value) for name, value in headers if name.lower() != b"content-length"]
                new_headers.append((b"content-type", b"application/json"))
                new_headers.append((b"content-length", str(len(new_body)).encode("utf-8")))

                await send(
                    {
                        "type": "http.response.start",
                        "status": status_code,
                        "headers": new_headers,
                    }
                )
                await send({"type": "http.response.body", "body": new_body})
            except (json.JSONDecodeError, ValueError):
                # If JSON parsing fails, send original response
                await send(
                    {
                        "type": "http.response.start",
                        "status": status_code,
                        "headers": headers,
                    }
                )
                for chunk in body_chunks:
                    await send({"type": "http.response.body", "body": chunk})
                await send({"type": "http.response.body", "body": b""})

        await self.app(scope, receive, send_wrapper)
