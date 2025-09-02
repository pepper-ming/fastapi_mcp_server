-- scripts/init_timescale.sql
-- 初始化 TimescaleDB

-- 建立時間序列分析相關表
CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;

-- 統計分析結果表
CREATE TABLE analysis_results (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    analysis_type VARCHAR(50) NOT NULL,
    input_data JSONB NOT NULL,
    results JSONB NOT NULL,
    execution_time_ms INTEGER,
    user_id VARCHAR(100),
    session_id VARCHAR(100)
);

-- 建立時間序列超表
SELECT create_hypertable('analysis_results', 'timestamp');

-- 時間序列資料表
CREATE TABLE timeseries_data (
    timestamp TIMESTAMPTZ NOT NULL,
    series_id VARCHAR(100) NOT NULL,
    value DOUBLE PRECISION NOT NULL,
    meta_data JSONB,
    PRIMARY KEY (timestamp, series_id)
);

SELECT create_hypertable('timeseries_data', 'timestamp');

-- 模型訓練記錄表
CREATE TABLE model_training_logs (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    model_name VARCHAR(100) NOT NULL,
    model_version VARCHAR(50),
    training_data_hash VARCHAR(64),
    hyperparameters JSONB,
    metrics JSONB,
    model_path VARCHAR(200),
    status VARCHAR(20) DEFAULT 'training'
);

SELECT create_hypertable('model_training_logs', 'timestamp');

-- 建立索引
CREATE INDEX idx_analysis_type ON analysis_results (analysis_type, timestamp DESC);
CREATE INDEX idx_series_id ON timeseries_data (series_id, timestamp DESC);
CREATE INDEX idx_model_name ON model_training_logs (model_name, timestamp DESC);