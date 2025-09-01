from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_mcp import FastApiMCP

from app.api.statistics import router as statistics_router
from app.api.monitoring import router as monitoring_router
from app.core.settings import get_settings
from app.core.mcp_config import MCPToolConfig
from app.core.logging import mcp_logger
settings = get_settings()
mcp_config = MCPToolConfig()

# 建立 FastAPI 應用程式
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="基於 Model Context Protocol 的統計分析與機器學習推論服務平台 - 第二週版本",
    debug=settings.debug,
)

# 添加 CORS 中介軟體
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
)

# 初始化 MCP 整合（使用優化配置）
mcp = FastApiMCP(
    app,
    name=settings.mcp_name,
    description=settings.mcp_description,
    include_tags=mcp_config.include_tags,
    describe_all_responses=mcp_config.describe_all_responses,
)


# 基礎路由
@app.get("/", tags=["基礎"])
async def root() -> dict[str, str]:
    """根端點 - 服務狀態"""
    return {
        "service": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "mcp_endpoint": "/mcp",
    }


@app.get("/health", tags=["基礎"])
async def health_check() -> dict[str, str]:
    """健康檢查端點"""
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version,
    }


# 應用程式事件處理器
@app.on_event("startup")
async def startup_event():
    """應用程式啟動事件"""
    mcp_logger.logger.info(f"FastAPI MCP Server 啟動 - 版本: {settings.app_version}")
    mcp_logger.logger.info(f"MCP 端點: http://{settings.host}:{settings.port}/mcp")
    mcp_logger.logger.info(f"監控端點: http://{settings.host}:{settings.port}/monitoring/mcp/metrics")

@app.on_event("shutdown") 
async def shutdown_event():
    """應用程式關閉事件"""
    final_metrics = mcp_logger.get_metrics()
    mcp_logger.logger.info(f"FastAPI MCP Server 關閉 - 最終統計: {final_metrics}")

# 包含 API 路由
app.include_router(statistics_router)
app.include_router(monitoring_router)

# 掛載 MCP 服務
mcp.mount()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        log_level="debug" if settings.debug else "info",
    )
