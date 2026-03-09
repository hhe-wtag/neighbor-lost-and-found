import re
from collections import defaultdict, deque
import time
from typing import Dict, Deque, Set

from starlette import status
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request, Response


class RateLimiterMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app,
        max_requests: int = 3,
        window_seconds: float = 1.0,
        excluded_paths: Set[str] = None,
        excluded_prefixes: tuple = None,
        excluded_patterns: list = None,
    ):
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.excluded_paths = excluded_paths or {"/health", "/metrics"}
        self.excluded_prefixes = excluded_prefixes or ("/static", "/images", "/media")
        self.excluded_patterns = [
            re.compile(p) for p in (excluded_patterns or [])
        ]
        self.rate_limit_records: Dict[str, Deque[float]] = defaultdict(deque)

    def _is_excluded(self, path: str) -> bool:
        if path in self.excluded_paths:
            return True
        if path.startswith(self.excluded_prefixes):
            return True
        if any(pattern.match(path) for pattern in self.excluded_patterns):
            return True
        return False

    async def dispatch(self, request: Request, call_next):
        if self._is_excluded(request.url.path):
            return await call_next(request)

        client_ip = request.client.host
        current_time = time.time()
        request_times = self.rate_limit_records[client_ip]

        while request_times and current_time - request_times[0] > self.window_seconds:
            request_times.popleft()

        if len(request_times) >= self.max_requests:
            retry_after = self.window_seconds - (current_time - request_times[0])
            return Response(
                f"Rate limit exceeded. Retry after {retry_after:.2f} seconds",
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                headers={"Retry-After": str(round(retry_after))},
            )

        request_times.append(current_time)
        response = await call_next(request)
        return response