from fastapi import APIRouter, HTTPException

from app.models.advanced_statistics import (
    CorrelationRequest,
    CorrelationResult,
    RegressionRequest,
    RegressionResult,
)
from app.services.advanced_statistics import AdvancedStatisticsService

router = APIRouter(prefix="/statistics/advanced", tags=["進階統計分析"])


@router.post(
    "/correlation",
    response_model=CorrelationResult,
    operation_id="calculate_correlation",
    summary="相關性分析",
    description="計算兩變數間的相關性，支援 Pearson、Spearman、Kendall 相關係數",
)
async def calculate_correlation(request: CorrelationRequest) -> CorrelationResult:
    """計算相關性分析"""
    try:
        return AdvancedStatisticsService.calculate_correlation(request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"相關性分析時發生錯誤: {str(e)}")


@router.post(
    "/regression",
    response_model=RegressionResult,
    operation_id="perform_regression",
    summary="迴歸分析",
    description="執行各種迴歸分析，包含線性、多項式、Ridge、Lasso 迴歸",
)
async def perform_regression(request: RegressionRequest) -> RegressionResult:
    """執行迴歸分析"""
    try:
        return AdvancedStatisticsService.perform_regression(request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"迴歸分析時發生錯誤: {str(e)}")
