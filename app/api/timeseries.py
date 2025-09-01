from fastapi import APIRouter, HTTPException

from app.models.timeseries import (
    AnomalyDetectionRequest,
    AnomalyDetectionResult,
    ForecastRequest,
    ForecastResult,
)
from app.services.timeseries import TimeSeriesService

router = APIRouter(prefix="/timeseries", tags=["時間序列分析"])


@router.post(
    "/forecast",
    response_model=ForecastResult,
    operation_id="forecast_timeseries",
    summary="時間序列預測",
    description="執行時間序列預測，支援線性趨勢、移動平均、指數平滑、ARIMA 模型",
)
async def forecast_timeseries(request: ForecastRequest) -> ForecastResult:
    """時間序列預測"""
    try:
        return TimeSeriesService.forecast_timeseries(request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"時間序列預測時發生錯誤: {str(e)}")


@router.post(
    "/anomaly-detection",
    response_model=AnomalyDetectionResult,
    operation_id="detect_timeseries_anomalies",
    summary="時間序列異常檢測",
    description="檢測時間序列中的異常點，支援統計方法、IQR、Z-score 檢測",
)
async def detect_anomalies(request: AnomalyDetectionRequest) -> AnomalyDetectionResult:
    """時間序列異常檢測"""
    try:
        return TimeSeriesService.detect_anomalies(request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"異常檢測時發生錯誤: {str(e)}")
