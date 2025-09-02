import asyncio
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import AsyncEngine

from alembic import context

from app.database.base import Base
from app.core.settings import get_settings

# 確保所有模型都被導入，這樣 Alembic 才能發現它們
from app.models.database import (
    AnalysisResult,
    TimeSeriesData, 
    ModelTrainingLog,
    StatisticsData,
    PerformanceMetrics,
    MCPRequestLog,
)

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config
settings = get_settings()

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = Base.metadata

# 設定資料庫 URL
config.set_main_option("sqlalchemy.url", settings.database_url)

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)
    
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations():
    """在非同步模式下運行遷移"""
    from sqlalchemy.ext.asyncio import create_async_engine
    
    connectable = create_async_engine(settings.database_url)
    
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    
    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    if settings.database_url.startswith("postgresql+asyncpg"):
        # 非同步資料庫連線
        asyncio.run(run_async_migrations())
    else:
        # 同步資料庫連線
        connectable = engine_from_config(
            config.get_section(config.config_ini_section, {}),
            prefix="sqlalchemy.",
            poolclass=pool.NullPool,
        )

        with connectable.connect() as connection:
            context.configure(
                connection=connection, target_metadata=target_metadata
            )

            with context.begin_transaction():
                context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
