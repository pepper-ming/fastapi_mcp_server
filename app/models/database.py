from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func

from app.database.base import Base


class AnalysisResult(Base):
    """統計分析結果模型"""

    __tablename__ = "analysis_results"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    analysis_type = Column(String(50), nullable=False, index=True)
    input_data = Column(JSONB, nullable=False)
    results = Column(JSONB, nullable=False)
    execution_time_ms = Column(Integer)
    user_id = Column(String(100), index=True)
    session_id = Column(String(100), index=True)


class TimeSeriesData(Base):
    """時間序列資料模型"""

    __tablename__ = "timeseries_data"

    timestamp = Column(DateTime(timezone=True), primary_key=True)
    series_id = Column(String(100), primary_key=True, index=True)
    value = Column(Float, nullable=False)
    metadata = Column(JSONB)


class ModelTrainingLog(Base):
    """模型訓練日誌模型"""

    __tablename__ = "model_training_logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    model_name = Column(String(100), nullable=False, index=True)
    model_version = Column(String(50))
    training_data_hash = Column(String(64))
    hyperparameters = Column(JSONB)
    metrics = Column(JSONB)
    model_path = Column(String(200))
    status = Column(String(20), default="training")


class StatisticsData(Base):
    """統計數據表 - 對應 TimescaleDB 中的 statistics_data"""

    __tablename__ = "statistics_data"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    data_type = Column(String(50), nullable=False, index=True)
    source_name = Column(String(100), nullable=False, index=True)
    metrics = Column(JSONB, nullable=False)
    metadata = Column(JSONB, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class PerformanceMetrics(Base):
    """性能監控數據表 - 對應 TimescaleDB 中的 performance_metrics"""

    __tablename__ = "performance_metrics"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    service_name = Column(String(100), nullable=False, index=True)
    metric_name = Column(String(100), nullable=False, index=True)
    metric_value = Column(Float, nullable=False)
    tags = Column(JSONB, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class MCPRequestLog(Base):
    """MCP 請求日誌表 - 對應 TimescaleDB 中的 mcp_request_logs"""

    __tablename__ = "mcp_request_logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    session_id = Column(String(100), nullable=False, index=True)
    action = Column(String(100), nullable=False, index=True)
    request_data = Column(JSONB, default={})
    response_data = Column(JSONB, default={})
    duration_ms = Column(Integer)
    success = Column(Boolean, nullable=False, default=True)
    error_message = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
