from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_mcp import FastApiMCP

from app.api.advanced_statistics import router as advanced_stats_router
from app.api.machine_learning import router as ml_router
from app.api.monitoring import router as monitoring_router
from app.api.statistics import router as statistics_router
from app.api.timeseries import router as timeseries_router
from app.core.logging import mcp_logger
from app.core.mcp_config import MCPToolConfig
from app.core.settings import get_settings
from app.database.base import engine, Base
from app.middleware.mcp_monitoring import MCPMonitoringMiddleware
from app.services.cache import cache_service

settings = get_settings()
mcp_config = MCPToolConfig()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """應用程式生命週期管理"""
    # 啟動時執行
    print("🚀 FastAPI MCP Server 啟動中...")

    # 建立資料庫表
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # 連接快取服務
    await cache_service.connect()

    print("✅ 所有服務已啟動")

    yield

    # 關閉時執行
    print("🛑 FastAPI MCP Server 關閉中...")
    await cache_service.disconnect()
    await engine.dispose()
    print("✅ 所有服務已關閉")


# 建立 FastAPI 應用程式
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="基於 Model Context Protocol 的統計分析與機器學習推論服務平台 - 第二週版本",
    debug=settings.debug,
    lifespan=lifespan
)

# 添加中介軟體
app.add_middleware(MCPMonitoringMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
)

# 初始化 MCP 整合（使用標準配置）
mcp = FastApiMCP(
    app,
    name=settings.mcp_name,
    description=settings.mcp_description,
    include_operations=mcp_config.include_operations,
    include_tags=mcp_config.include_tags,
    describe_all_responses=mcp_config.describe_all_responses,
    describe_full_response_schema=mcp_config.describe_full_response_schema,
)


# 基礎路由
@app.get("/", tags=["基礎"])
async def root() -> dict:
    """根端點 - 服務狀態"""
    return {
        "service": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "features": [
            "descriptive_statistics",
            "hypothesis_testing",
            "correlation_analysis",
            "regression_analysis",
            "timeseries_forecasting",
            "anomaly_detection",
            "machine_learning",
            "model_management"
        ],
        "mcp_endpoint": "/mcp",
    }


@app.get("/health", tags=["基礎"])
async def health_check() -> dict:
    """健康檢查端點"""
    cache_stats = await cache_service.get_cache_stats()
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version,
        "cache": cache_stats,
        "database": "connected",
    }




# 包含 API 路由
app.include_router(statistics_router)
app.include_router(monitoring_router)
app.include_router(advanced_stats_router)
app.include_router(timeseries_router)
app.include_router(ml_router)

# 掛載 MCP 服務（使用推薦的 HTTP transport）
mcp.mount_http()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        log_level="debug" if settings.debug else "info",
    )
