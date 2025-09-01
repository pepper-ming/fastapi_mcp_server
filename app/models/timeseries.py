from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class TimeSeriesFrequency(str, Enum):
    """時間序列頻率"""

    DAILY = "D"
    WEEKLY = "W"
    MONTHLY = "M"
    QUARTERLY = "Q"
    YEARLY = "Y"
    HOURLY = "H"


class ForecastModel(str, Enum):
    """預測模型類型"""

    ARIMA = "arima"
    EXPONENTIAL_SMOOTHING = "exponential_smoothing"
    LINEAR_TREND = "linear_trend"
    MOVING_AVERAGE = "moving_average"


class TimeSeriesPoint(BaseModel):
    """時間序列資料點"""

    timestamp: datetime = Field(..., description="時間戳記")
    value: float = Field(..., description="數值")


class TimeSeriesData(BaseModel):
    """時間序列資料"""

    series_id: str = Field(..., description="序列識別碼")
    data: list[TimeSeriesPoint] = Field(
        ..., description="時間序列資料點", min_length=10
    )
    frequency: Optional[TimeSeriesFrequency] = Field(
        default=None, description="資料頻率"
    )
    metadata: Optional[dict[str, Any]] = Field(default={}, description="額外資訊")


class ForecastRequest(BaseModel):
    """預測請求"""

    timeseries: TimeSeriesData = Field(..., description="時間序列資料")
    model_type: ForecastModel = Field(
        default=ForecastModel.LINEAR_TREND, description="預測模型"
    )
    forecast_periods: int = Field(default=10, ge=1, le=100, description="預測期數")
    confidence_level: float = Field(
        default=0.95, ge=0.01, le=0.99, description="信賴水準"
    )

    # ARIMA 參數
    arima_order: Optional[tuple] = Field(
        default=(1, 1, 1), description="ARIMA 階數 (p,d,q)"
    )

    # 移動平均參數
    ma_window: Optional[int] = Field(default=5, ge=2, le=20, description="移動平均視窗")


class ForecastResult(BaseModel):
    """預測結果"""

    series_id: str = Field(description="序列識別碼")
    model_type: str = Field(description="使用的模型類型")
    forecast_values: list[float] = Field(description="預測值")
    forecast_dates: list[datetime] = Field(description="預測時間點")
    confidence_intervals: list[dict[str, float]] = Field(description="信賴區間")
    model_metrics: dict[str, float] = Field(description="模型評估指標")
    model_summary: str = Field(description="模型摘要")


class AnomalyDetectionRequest(BaseModel):
    """異常檢測請求"""

    timeseries: TimeSeriesData = Field(..., description="時間序列資料")
    detection_method: str = Field(
        default="statistical", description="檢測方法: statistical, iqr, zscore"
    )
    sensitivity: float = Field(default=2.0, ge=1.0, le=5.0, description="敏感度")
    window_size: Optional[int] = Field(
        default=10, ge=5, le=50, description="滑動視窗大小"
    )


class AnomalyPoint(BaseModel):
    """異常點"""

    timestamp: datetime = Field(description="異常時間點")
    value: float = Field(description="異常值")
    anomaly_score: float = Field(description="異常分數")
    expected_range: dict[str, float] = Field(description="預期範圍")


class AnomalyDetectionResult(BaseModel):
    """異常檢測結果"""

    series_id: str = Field(description="序列識別碼")
    detection_method: str = Field(description="檢測方法")
    anomaly_points: list[AnomalyPoint] = Field(description="異常點列表")
    anomaly_rate: float = Field(description="異常率")
    summary: str = Field(description="檢測摘要")
