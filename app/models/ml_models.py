from datetime import datetime
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field
from enum import Enum
import uuid


class ModelType(str, Enum):
    """模型類型"""
    CLASSIFICATION = "classification"
    REGRESSION = "regression"
    CLUSTERING = "clustering"
    ANOMALY_DETECTION = "anomaly_detection"


class ModelStatus(str, Enum):
    """模型狀態"""
    TRAINING = "training"
    TRAINED = "trained"
    DEPLOYED = "deployed"
    DEPRECATED = "deprecated"
    FAILED = "failed"


class ModelMetadata(BaseModel):
    """模型元資料"""
    model_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="模型唯一識別碼")
    model_name: str = Field(..., description="模型名稱")
    model_type: ModelType = Field(..., description="模型類型")
    version: str = Field(..., description="模型版本")
    description: Optional[str] = Field(default=None, description="模型描述")

    # 訓練資訊
    training_data_hash: Optional[str] = Field(default=None, description="訓練資料哈希值")
    hyperparameters: Dict[str, Any] = Field(default={}, description="超參數")

    # 評估指標
    metrics: Dict[str, float] = Field(default={}, description="模型評估指標")

    # 狀態與時間戳
    status: ModelStatus = Field(default=ModelStatus.TRAINING, description="模型狀態")
    created_at: datetime = Field(default_factory=datetime.now, description="建立時間")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新時間")

    # 儲存路徑
    model_path: Optional[str] = Field(default=None, description="模型檔案路徑")

    # 標籤
    tags: List[str] = Field(default=[], description="模型標籤")


class TrainingRequest(BaseModel):
    """模型訓練請求"""
    model_name: str = Field(..., description="模型名稱")
    model_type: ModelType = Field(..., description="模型類型")
    algorithm: str = Field(..., description="機器學習算法")

    # 訓練資料
    training_data: List[List[Union[int, float]]] = Field(..., description="訓練特徵資料")
    training_labels: List[Union[int, float, str]] = Field(..., description="訓練標籤")

    # 超參數
    hyperparameters: Dict[str, Any] = Field(default={}, description="超參數設定")

    # 驗證設定
    validation_split: float = Field(default=0.2, ge=0.1, le=0.5, description="驗證資料比例")
    random_state: int = Field(default=42, description="隨機種子")

    # 元資料
    description: Optional[str] = Field(default=None, description="訓練描述")
    tags: List[str] = Field(default=[], description="模型標籤")


class PredictionRequest(BaseModel):
    """預測請求"""
    model_id: str = Field(..., description="模型ID")
    input_data: List[List[Union[int, float]]] = Field(..., description="輸入特徵資料", min_length=1)
    return_probabilities: bool = Field(default=False, description="是否返回機率 (分類模型)")


class TrainingResult(BaseModel):
    """訓練結果"""
    model_id: str = Field(description="模型ID")
    model_metadata: ModelMetadata = Field(description="模型元資料")
    training_metrics: Dict[str, float] = Field(description="訓練指標")
    validation_metrics: Dict[str, float] = Field(description="驗證指標")
    training_time_seconds: float = Field(description="訓練時間(秒)")


class PredictionResult(BaseModel):
    """預測結果"""
    model_id: str = Field(description="使用的模型ID")
    predictions: List[Union[int, float, str]] = Field(description="預測結果")
    probabilities: Optional[List[List[float]]] = Field(default=None, description="預測機率 (如適用)")
    prediction_time_ms: float = Field(description="預測時間(毫秒)")


class ModelListItem(BaseModel):
    """模型列表項目"""
    model_id: str = Field(description="模型ID")
    model_name: str = Field(description="模型名稱")
    model_type: ModelType = Field(description="模型類型")
    version: str = Field(description="模型版本")
    status: ModelStatus = Field(description="模型狀態")
    created_at: datetime = Field(description="建立時間")
    tags: List[str] = Field(description="模型標籤")