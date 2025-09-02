from typing import List, Optional
from fastapi import APIRouter, HTTPException

from app.models.ml_models import (
    TrainingRequest, TrainingResult,
    PredictionRequest, PredictionResult,
    ModelMetadata, ModelListItem, ModelType
)
from app.services.model_manager import model_manager

router = APIRouter(prefix="/ml", tags=["機器學習"])


@router.post(
    "/train",
    response_model=TrainingResult,
    operation_id="train_model",
    summary="訓練機器學習模型",
    description="訓練新的機器學習模型，支援分類、迴歸、聚類算法"
)
async def train_model(request: TrainingRequest) -> TrainingResult:
    """訓練機器學習模型"""
    try:
        return await model_manager.train_model(request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"模型訓練時發生錯誤: {str(e)}"
        )


@router.post(
    "/predict",
    response_model=PredictionResult,
    operation_id="make_prediction",
    summary="執行模型預測",
    description="使用訓練好的模型進行預測"
)
async def make_prediction(request: PredictionRequest) -> PredictionResult:
    """執行模型預測"""
    try:
        return await model_manager.predict(request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"預測時發生錯誤: {str(e)}"
        )


@router.get(
    "/models",
    response_model=List[ModelListItem],
    operation_id="list_models",
    summary="列出所有模型",
    description="獲取所有已訓練模型的列表和元資料"
)
async def list_models(model_type: Optional[ModelType] = None) -> List[ModelListItem]:
    """列出所有模型"""
    try:
        return await model_manager.list_models(model_type)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"列出模型時發生錯誤: {str(e)}"
        )


@router.get(
    "/models/{model_id}",
    response_model=ModelMetadata,
    operation_id="get_model_metadata",
    summary="獲取模型元資料",
    description="獲取指定模型的詳細元資料"
)
async def get_model_metadata(model_id: str) -> ModelMetadata:
    """獲取模型元資料"""
    try:
        metadata = await model_manager.get_model_metadata(model_id)
        if metadata is None:
            raise HTTPException(status_code=404, detail=f"找不到模型: {model_id}")
        return metadata
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"獲取模型元資料時發生錯誤: {str(e)}"
        )


@router.delete(
    "/models/{model_id}",
    operation_id="delete_model",
    summary="刪除模型",
    description="刪除指定的機器學習模型和其元資料"
)
async def delete_model(model_id: str) -> dict:
    """刪除模型"""
    try:
        success = await model_manager.delete_model(model_id)
        if not success:
            raise HTTPException(status_code=404, detail=f"找不到模型: {model_id}")
        return {"message": f"成功刪除模型: {model_id}"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"刪除模型時發生錯誤: {str(e)}"
        )