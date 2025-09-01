-- TimescaleDB 初始化腳本
-- 確保 TimescaleDB 擴展可用

-- 創建 TimescaleDB 擴展
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- 創建 TimescaleDB Toolkit 擴展（用於高級分析功能）
CREATE EXTENSION IF NOT EXISTS timescaledb_toolkit;

-- 創建 PostGIS 擴展（用於地理空間數據）
CREATE EXTENSION IF NOT EXISTS postgis;

-- 創建 UUID 擴展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 設置時區
SET timezone = 'UTC';

-- 創建應用程式用戶
CREATE USER fastapi_user WITH PASSWORD 'fastapi_password';

-- 授予必要權限
GRANT CONNECT ON DATABASE fastapi_mcp TO fastapi_user;
GRANT USAGE ON SCHEMA public TO fastapi_user;
GRANT CREATE ON SCHEMA public TO fastapi_user;

-- 創建統計數據表
CREATE TABLE IF NOT EXISTS statistics_data (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    data_type VARCHAR(50) NOT NULL,
    source_name VARCHAR(100) NOT NULL,
    metrics JSONB NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 將統計數據表轉換為 hypertable
SELECT create_hypertable('statistics_data', 'timestamp', if_not_exists => TRUE);

-- 創建性能監控數據表
CREATE TABLE IF NOT EXISTS performance_metrics (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    service_name VARCHAR(100) NOT NULL,
    metric_name VARCHAR(100) NOT NULL,
    metric_value DOUBLE PRECISION NOT NULL,
    tags JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 將性能監控表轉換為 hypertable
SELECT create_hypertable('performance_metrics', 'timestamp', if_not_exists => TRUE);

-- 創建 MCP 請求日誌表
CREATE TABLE IF NOT EXISTS mcp_request_logs (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    session_id VARCHAR(100) NOT NULL,
    action VARCHAR(100) NOT NULL,
    request_data JSONB DEFAULT '{}',
    response_data JSONB DEFAULT '{}',
    duration_ms INTEGER,
    success BOOLEAN NOT NULL DEFAULT TRUE,
    error_message TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 將 MCP 請求日誌表轉換為 hypertable
SELECT create_hypertable('mcp_request_logs', 'timestamp', if_not_exists => TRUE);

-- 創建時間序列分析表（為第11天準備）
CREATE TABLE IF NOT EXISTS time_series_data (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL,
    series_name VARCHAR(100) NOT NULL,
    value DOUBLE PRECISION NOT NULL,
    attributes JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 將時間序列數據表轉換為 hypertable
SELECT create_hypertable('time_series_data', 'timestamp', if_not_exists => TRUE);

-- 創建索引以優化查詢性能
CREATE INDEX IF NOT EXISTS idx_statistics_data_type ON statistics_data (data_type, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_statistics_source ON statistics_data (source_name, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_performance_service ON performance_metrics (service_name, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_performance_metric ON performance_metrics (metric_name, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_mcp_session ON mcp_request_logs (session_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_mcp_action ON mcp_request_logs (action, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_time_series_name ON time_series_data (series_name, timestamp DESC);

-- 使用 JSONB GIN 索引優化 JSON 查詢
CREATE INDEX IF NOT EXISTS idx_statistics_metrics_gin ON statistics_data USING GIN (metrics);
CREATE INDEX IF NOT EXISTS idx_performance_tags_gin ON performance_metrics USING GIN (tags);
CREATE INDEX IF NOT EXISTS idx_mcp_request_gin ON mcp_request_logs USING GIN (request_data);
CREATE INDEX IF NOT EXISTS idx_time_series_attrs_gin ON time_series_data USING GIN (attributes);

-- 授予表權限給應用程式用戶
GRANT ALL PRIVILEGES ON TABLE statistics_data TO fastapi_user;
GRANT ALL PRIVILEGES ON TABLE performance_metrics TO fastapi_user;
GRANT ALL PRIVILEGES ON TABLE mcp_request_logs TO fastapi_user;
GRANT ALL PRIVILEGES ON TABLE time_series_data TO fastapi_user;

-- 授予序列權限
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO fastapi_user;

-- 設置資料保留策略（保留30天的數據）
SELECT add_retention_policy('statistics_data', INTERVAL '30 days', if_not_exists => TRUE);
SELECT add_retention_policy('performance_metrics', INTERVAL '30 days', if_not_exists => TRUE);
SELECT add_retention_policy('mcp_request_logs', INTERVAL '7 days', if_not_exists => TRUE);

-- 創建壓縮策略（7天後壓縮數據）
SELECT add_compression_policy('statistics_data', INTERVAL '7 days', if_not_exists => TRUE);
SELECT add_compression_policy('performance_metrics', INTERVAL '7 days', if_not_exists => TRUE);
SELECT add_compression_policy('time_series_data', INTERVAL '7 days', if_not_exists => TRUE);

-- 創建連續聚合視圖（小時級別統計）
CREATE MATERIALIZED VIEW IF NOT EXISTS statistics_hourly
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 hour', timestamp) AS bucket,
    data_type,
    source_name,
    COUNT(*) as record_count,
    jsonb_agg(metrics) as aggregated_metrics
FROM statistics_data
GROUP BY bucket, data_type, source_name
WITH NO DATA;

-- 創建連續聚合視圖的刷新策略
SELECT add_continuous_aggregate_policy('statistics_hourly',
    start_offset => INTERVAL '1 day',
    end_offset => INTERVAL '1 hour',
    schedule_interval => INTERVAL '1 hour',
    if_not_exists => TRUE);

-- 輸出設置完成信息
DO $$
BEGIN
    RAISE NOTICE 'TimescaleDB 初始化完成！';
    RAISE NOTICE '- 已創建並配置 4 個 hypertable';
    RAISE NOTICE '- 已設置性能優化索引';
    RAISE NOTICE '- 已配置數據保留和壓縮策略';
    RAISE NOTICE '- 已創建連續聚合視圖';
    RAISE NOTICE '- 已授予應用程式用戶權限';
END
$$;
