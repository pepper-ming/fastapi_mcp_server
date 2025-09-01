from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """應用程式設定"""

    model_config = SettingsConfigDict(
        env_file=".env", env_ignore_empty=True, extra="ignore"
    )

    # 應用程式設定
    app_name: str = "FastAPI MCP Server"
    app_version: str = "0.1.0"
    debug: bool = False

    # 伺服器設定
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = False

    # 資料庫設定
    database_url: str = Field(
        default="sqlite:///./app.db", description="資料庫連線 URL"
    )
    database_echo: bool = False

    # Redis 設定
    redis_url: str = Field(
        default="redis://localhost:6379/0", description="Redis 連線 URL"
    )

    # MCP 設定
    mcp_name: str = "Statistical Analysis MCP"
    mcp_description: str = "統計分析與機器學習推論服務"
    mcp_version: str = "1.0.0"

    # CORS 設定
    cors_origins: list[str] = ["*"]
    cors_allow_credentials: bool = True
    cors_allow_methods: list[str] = ["*"]
    cors_allow_headers: list[str] = ["*"]


@lru_cache
def get_settings() -> Settings:
    """獲取應用程式設定（含快取）"""
    return Settings()
