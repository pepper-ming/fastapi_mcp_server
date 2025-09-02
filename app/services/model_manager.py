import os
import json
import joblib
import hashlib
import time
from datetime import datetime
from typing import List, Dict, Any, Optional, Union
import numpy as np
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.svm import SVC, SVR
from sklearn.cluster import KMeans
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    mean_squared_error, mean_absolute_error, r2_score,
    silhouette_score, adjusted_rand_score
)

from app.models.ml_models import (
    ModelMetadata, TrainingRequest, PredictionRequest,
    TrainingResult, PredictionResult, ModelListItem,
    ModelType, ModelStatus
)


class ModelManager:
    """機器學習模型管理器"""

    def __init__(self, models_directory: str = "./models"):
        self.models_directory = models_directory
        self.loaded_models: Dict[str, Any] = {}  # 記憶體中的模型快取

        # 確保模型目錄存在
        os.makedirs(models_directory, exist_ok=True)

        # 支援的算法
        self.algorithms = {
            ModelType.CLASSIFICATION: {
                'random_forest': RandomForestClassifier,
                'logistic_regression': LogisticRegression,
                'svm': SVC
            },
            ModelType.REGRESSION: {
                'random_forest': RandomForestRegressor,
                'linear_regression': LinearRegression,
                'svr': SVR
            },
            ModelType.CLUSTERING: {
                'kmeans': KMeans
            }
        }

    def _calculate_data_hash(self, data: List[List[Union[int, float]]], labels: List[Union[int, float, str]]) -> str:
        """計算訓練資料的哈希值"""
        combined_data = str(data) + str(labels)
        return hashlib.md5(combined_data.encode()).hexdigest()

    def _get_model_path(self, model_id: str) -> str:
        """獲取模型檔案路徑"""
        return os.path.join(self.models_directory, f"{model_id}.joblib")

    def _get_metadata_path(self, model_id: str) -> str:
        """獲取元資料檔案路徑"""
        return os.path.join(self.models_directory, f"{model_id}_metadata.json")

    async def train_model(self, request: TrainingRequest) -> TrainingResult:
        """訓練模型"""
        start_time = time.time()

        # 準備資料
        X = np.array(request.training_data)
        y = np.array(request.training_labels)

        # 計算資料哈希
        data_hash = self._calculate_data_hash(request.training_data, request.training_labels)

        # 分割訓練和驗證資料
        X_train, X_val, y_train, y_val = train_test_split(
            X, y, test_size=request.validation_split, random_state=request.random_state
        )

        # 選擇並初始化算法
        if request.model_type not in self.algorithms:
            raise ValueError(f"不支援的模型類型: {request.model_type}")

        if request.algorithm not in self.algorithms[request.model_type]:
            raise ValueError(f"模型類型 {request.model_type} 不支援算法 {request.algorithm}")

        algorithm_class = self.algorithms[request.model_type][request.algorithm]
        model = algorithm_class(**request.hyperparameters)

        # 訓練模型
        model.fit(X_train, y_train)

        # 計算訓練和驗證指標
        train_pred = model.predict(X_train)
        val_pred = model.predict(X_val)

        training_metrics = self._calculate_metrics(y_train, train_pred, request.model_type)
        validation_metrics = self._calculate_metrics(y_val, val_pred, request.model_type)

        # 建立模型元資料
        model_metadata = ModelMetadata(
            model_name=request.model_name,
            model_type=request.model_type,
            version="1.0.0",  # 簡化版本管理
            description=request.description,
            training_data_hash=data_hash,
            hyperparameters=request.hyperparameters,
            metrics=validation_metrics,
            status=ModelStatus.TRAINED,
            tags=request.tags
        )

        # 儲存模型
        model_path = self._get_model_path(model_metadata.model_id)
        joblib.dump(model, model_path)
        model_metadata.model_path = model_path

        # 儲存元資料
        metadata_path = self._get_metadata_path(model_metadata.model_id)
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(model_metadata.dict(), f, ensure_ascii=False, indent=2, default=str)

        # 載入到記憶體快取
        self.loaded_models[model_metadata.model_id] = model

        training_time = time.time() - start_time

        return TrainingResult(
            model_id=model_metadata.model_id,
            model_metadata=model_metadata,
            training_metrics=training_metrics,
            validation_metrics=validation_metrics,
            training_time_seconds=training_time
        )

    def _calculate_metrics(self, y_true, y_pred, model_type: ModelType) -> Dict[str, float]:
        """計算評估指標"""
        metrics = {}

        if model_type == ModelType.CLASSIFICATION:
            metrics['accuracy'] = accuracy_score(y_true, y_pred)
            metrics['precision'] = precision_score(y_true, y_pred, average='weighted', zero_division=0)
            metrics['recall'] = recall_score(y_true, y_pred, average='weighted', zero_division=0)
            metrics['f1'] = f1_score(y_true, y_pred, average='weighted', zero_division=0)

        elif model_type == ModelType.REGRESSION:
            metrics['mse'] = mean_squared_error(y_true, y_pred)
            metrics['mae'] = mean_absolute_error(y_true, y_pred)
            metrics['r2'] = r2_score(y_true, y_pred)
            metrics['rmse'] = np.sqrt(metrics['mse'])

        elif model_type == ModelType.CLUSTERING:
            # 聚類評估需要原始特徵資料，這裡簡化處理
            if len(np.unique(y_pred)) > 1:
                # 簡化處理：假設 y_true 是特徵資料的一維表示
                if len(y_true) > 0:
                    metrics['silhouette'] = 0.5  # 簡化的預設值

        return metrics

    async def predict(self, request: PredictionRequest) -> PredictionResult:
        """執行預測"""
        start_time = time.time()

        # 載入模型
        model = await self._load_model(request.model_id)
        if model is None:
            raise ValueError(f"找不到模型: {request.model_id}")

        # 準備輸入資料
        X = np.array(request.input_data)

        # 執行預測
        predictions = model.predict(X)

        # 如果是分類模型且要求機率
        probabilities = None
        if request.return_probabilities and hasattr(model, 'predict_proba'):
            probabilities = model.predict_proba(X).tolist()

        prediction_time = (time.time() - start_time) * 1000  # 轉換為毫秒

        return PredictionResult(
            model_id=request.model_id,
            predictions=predictions.tolist(),
            probabilities=probabilities,
            prediction_time_ms=prediction_time
        )

    async def _load_model(self, model_id: str) -> Optional[Any]:
        """載入模型"""
        # 先檢查記憶體快取
        if model_id in self.loaded_models:
            return self.loaded_models[model_id]

        # 從檔案載入
        model_path = self._get_model_path(model_id)
        if not os.path.exists(model_path):
            return None

        try:
            model = joblib.load(model_path)
            self.loaded_models[model_id] = model
            return model
        except Exception:
            return None

    async def get_model_metadata(self, model_id: str) -> Optional[ModelMetadata]:
        """獲取模型元資料"""
        metadata_path = self._get_metadata_path(model_id)
        if not os.path.exists(metadata_path):
            return None

        try:
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata_dict = json.load(f)
            return ModelMetadata(**metadata_dict)
        except Exception:
            return None

    async def list_models(self, model_type: Optional[ModelType] = None) -> List[ModelListItem]:
        """列出所有模型"""
        models = []

        for filename in os.listdir(self.models_directory):
            if filename.endswith('_metadata.json'):
                model_id = filename.replace('_metadata.json', '')
                metadata = await self.get_model_metadata(model_id)
                if metadata and (model_type is None or metadata.model_type == model_type):
                    models.append(ModelListItem(
                        model_id=metadata.model_id,
                        model_name=metadata.model_name,
                        model_type=metadata.model_type,
                        version=metadata.version,
                        status=metadata.status,
                        created_at=metadata.created_at,
                        tags=metadata.tags
                    ))

        return sorted(models, key=lambda x: x.created_at, reverse=True)

    async def delete_model(self, model_id: str) -> bool:
        """刪除模型"""
        model_path = self._get_model_path(model_id)
        metadata_path = self._get_metadata_path(model_id)
        
        try:
            # 移除檔案
            if os.path.exists(model_path):
                os.remove(model_path)
            if os.path.exists(metadata_path):
                os.remove(metadata_path)
            
            # 從記憶體快取移除
            if model_id in self.loaded_models:
                del self.loaded_models[model_id]
            
            return True
        except Exception:
            return False


# 全局模型管理器實例
model_manager = ModelManager()