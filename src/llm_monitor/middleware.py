import time

from fastapi import Request
from loguru import logger


async def telemetry_middleware(request: Request, call_next):
    """Intercepts requests to log latency and endpoint details."""
    start_time = time.time()
    response = await call_next(request)
    duration_ms = (time.time() - start_time) * 1000.0
    logger.info(
        "API Access: {} | Method: {} | Latency: {:.2f}ms | Status: {}",
        request.url.path,
        request.method,
        duration_ms,
        response.status_code,
    )
    return response
