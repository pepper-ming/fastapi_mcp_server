import logging
import time

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class MCPMonitoringMiddleware(BaseHTTPMiddleware):
    """MCP 請求監控中介軟體"""

    async def dispatch(self, request: Request, call_next):
        # 記錄 MCP 相關請求
        if request.url.path.startswith("/mcp"):
            start_time = time.time()

            logger.info(
                f"MCP request started: {request.method} {request.url.path}",
                extra={
                    "mcp_request": True,
                    "method": request.method,
                    "path": request.url.path,
                    "client_ip": request.client.host if request.client else "unknown",
                },
            )

            response: Response = await call_next(request)

            process_time = time.time() - start_time
            logger.info(
                f"MCP request completed: {response.status_code} in {process_time:.3f}s",
                extra={
                    "mcp_request": True,
                    "status_code": response.status_code,
                    "process_time": process_time,
                },
            )

            return response

        return await call_next(request)
