import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class TestWeek2Features:
    """第二週功能整合測試"""

    def test_advanced_statistics_correlation(self):
        """測試相關性分析"""
        payload = {
            "x_data": [1, 2, 3, 4, 5],
            "y_data": [2, 4, 6, 8, 10],
            "correlation_type": "pearson",
            "alpha": 0.05
        }

        response = client.post("/statistics/advanced/correlation", json=payload)
        assert response.status_code == 200

        data = response.json()
        assert "correlation_coefficient" in data
        assert "p_value" in data
        assert abs(data["correlation_coefficient"] - 1.0) < 0.01  # 完美正相關

    def test_regression_analysis(self):
        """測試迴歸分析"""
        payload = {
            "x_data": [1, 2, 3, 4, 5],
            "y_data": [2, 4, 6, 8, 10],
            "regression_type": "linear"
        }

        response = client.post("/statistics/advanced/regression", json=payload)
        assert response.status_code == 200

        data = response.json()
        assert "r_squared" in data
        assert "coefficients" in data
        assert data["r_squared"] > 0.9  # 高解釋力

    def test_timeseries_forecast(self):
        """測試時間序列預測"""
        payload = {
            "timeseries": {
                "series_id": "test_series",
                "data": [
                    {"timestamp": "2024-01-01T00:00:00", "value": 100},
                    {"timestamp": "2024-01-02T00:00:00", "value": 105},
                    {"timestamp": "2024-01-03T00:00:00", "value": 110},
                    {"timestamp": "2024-01-04T00:00:00", "value": 115},
                    {"timestamp": "2024-01-05T00:00:00", "value": 120},
                    {"timestamp": "2024-01-06T00:00:00", "value": 125},
                    {"timestamp": "2024-01-07T00:00:00", "value": 130},
                    {"timestamp": "2024-01-08T00:00:00", "value": 135},
                    {"timestamp": "2024-01-09T00:00:00", "value": 140},
                    {"timestamp": "2024-01-10T00:00:00", "value": 145}
                ]
            },
            "model_type": "linear_trend",
            "forecast_periods": 5
        }

        response = client.post("/timeseries/forecast", json=payload)
        assert response.status_code == 200

        data = response.json()
        assert "forecast_values" in data
        assert len(data["forecast_values"]) == 5

    def test_machine_learning_training(self):
        """測試機器學習模型訓練"""
        payload = {
            "model_name": "test_classifier",
            "model_type": "classification",
            "algorithm": "random_forest",
            "training_data": [[1, 2], [2, 3], [3, 4], [4, 5], [5, 6]],
            "training_labels": [0, 0, 1, 1, 1],
            "hyperparameters": {"n_estimators": 10, "random_state": 42}
        }

        response = client.post("/ml/train", json=payload)
        assert response.status_code == 200

        data = response.json()
        assert "model_id" in data
        assert "training_metrics" in data

        # 測試預測
        model_id = data["model_id"]
        prediction_payload = {
            "model_id": model_id,
            "input_data": [[1, 2], [5, 6]]
        }

        pred_response = client.post("/ml/predict", json=prediction_payload)
        assert pred_response.status_code == 200

        pred_data = pred_response.json()
        assert "predictions" in pred_data
        assert len(pred_data["predictions"]) == 2

    def test_health_check_enhanced(self):
        """測試增強的健康檢查"""
        response = client.get("/health")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "healthy"
        assert "cache" in data
        assert "database" in data

    def test_root_endpoint_features(self):
        """測試根端點顯示新功能"""
        response = client.get("/")
        assert response.status_code == 200

        data = response.json()
        assert "features" in data
        features = data["features"]
        
        # 檢查所有第二週新增的功能
        expected_features = [
            "descriptive_statistics",
            "hypothesis_testing", 
            "correlation_analysis",
            "regression_analysis",
            "timeseries_forecasting",
            "anomaly_detection",
            "machine_learning",
            "model_management"
        ]
        
        for feature in expected_features:
            assert feature in features

    def test_ml_models_list(self):
        """測試模型列表API"""
        response = client.get("/ml/models")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)

    def test_timeseries_anomaly_detection(self):
        """測試時間序列異常檢測"""
        payload = {
            "timeseries": {
                "series_id": "anomaly_test_series",
                "data": [
                    {"timestamp": "2024-01-01T00:00:00", "value": 100},
                    {"timestamp": "2024-01-02T00:00:00", "value": 105},
                    {"timestamp": "2024-01-03T00:00:00", "value": 500},  # 異常值
                    {"timestamp": "2024-01-04T00:00:00", "value": 110},
                    {"timestamp": "2024-01-05T00:00:00", "value": 115},
                    {"timestamp": "2024-01-06T00:00:00", "value": 120},
                    {"timestamp": "2024-01-07T00:00:00", "value": 125},
                    {"timestamp": "2024-01-08T00:00:00", "value": 130},
                    {"timestamp": "2024-01-09T00:00:00", "value": 135},
                    {"timestamp": "2024-01-10T00:00:00", "value": 140}
                ]
            },
            "detection_method": "statistical",
            "sensitivity": 2.0
        }

        response = client.post("/timeseries/anomaly-detection", json=payload)
        assert response.status_code == 200

        data = response.json()
        assert "anomaly_points" in data
        assert "anomaly_rate" in data
        assert len(data["anomaly_points"]) > 0  # 應該檢測到異常點