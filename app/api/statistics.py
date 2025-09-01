from fastapi import APIRouter, HTTPException

from app.models.statistics import (
    DescriptiveStatistics,
    HypothesisTestRequest,
    HypothesisTestResult,
    StatisticalDataRequest,
)
from app.services.statistics import StatisticsService

router = APIRouter(prefix="/statistics", tags=["統計分析"])


@router.post(
    "/descriptive",
    response_model=DescriptiveStatistics,
    operation_id="calculate_descriptive_statistics",
    summary="計算描述性統計",
    description="計算給定資料的完整描述性統計，包含中心趨勢、變異度量、分布形狀等指標",
)
async def calculate_descriptive_statistics(
    request: StatisticalDataRequest,
) -> DescriptiveStatistics:
    """計算描述性統計量"""
    try:
        return StatisticsService.calculate_descriptive_statistics(
            data=request.data, confidence_level=request.confidence_level
        )
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"計算描述性統計時發生錯誤: {str(e)}"
        )


@router.post(
    "/hypothesis-test",
    response_model=HypothesisTestResult,
    operation_id="perform_hypothesis_test",
    summary="執行假設檢定",
    description="執行各種統計假設檢定，包含單樣本 t 檢定等",
)
async def perform_hypothesis_test(
    request: HypothesisTestRequest,
) -> HypothesisTestResult:
    """執行假設檢定"""
    try:
        return StatisticsService.perform_hypothesis_test(request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"執行假設檢定時發生錯誤: {str(e)}")


@router.get(
    "/supported-tests",
    operation_id="get_supported_tests",
    summary="取得支援的檢定類型",
    description="列出目前支援的所有統計檢定類型",
)
async def get_supported_tests() -> dict[str, list[dict[str, str]]]:
    """取得支援的檢定類型"""
    return {
        "supported_tests": [
            {
                "type": "one_sample_t",
                "name": "單樣本 t 檢定",
                "description": "檢定單一樣本平均數是否等於特定數值",
            }
        ]
    }
