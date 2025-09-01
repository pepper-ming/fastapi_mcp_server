from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


class TestStatisticsAPI:
    """統計 API 整合測試"""

    def test_root_endpoint(self):
        """測試根端點"""
        response = client.get("/")
        assert response.status_code == 200

        data = response.json()
        assert "service" in data
        assert "version" in data
        assert "status" in data
        assert data["status"] == "running"

    def test_health_check(self):
        """測試健康檢查端點"""
        response = client.get("/health")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "healthy"

    def test_descriptive_statistics_endpoint(self):
        """測試描述性統計端點"""
        payload = {"data": [1, 2, 3, 4, 5], "confidence_level": 0.95}

        response = client.post("/statistics/descriptive", json=payload)
        assert response.status_code == 200

        data = response.json()
        assert "count" in data
        assert "mean" in data
        assert "median" in data
        assert data["count"] == 5
        assert data["mean"] == 3.0

    def test_hypothesis_test_endpoint(self):
        """測試假設檢定端點"""
        payload = {
            "sample_data": [2.1, 2.3, 1.9, 2.0, 2.2],
            "test_type": "one_sample_t",
            "null_hypothesis_value": 2.0,
            "alternative": "two_sided",
            "alpha": 0.05,
        }

        response = client.post("/statistics/hypothesis-test", json=payload)
        assert response.status_code == 200

        data = response.json()
        assert "test_statistic" in data
        assert "p_value" in data
        assert "reject_null" in data

    def test_supported_tests_endpoint(self):
        """測試支援的檢定類型端點"""
        response = client.get("/statistics/supported-tests")
        assert response.status_code == 200

        data = response.json()
        assert "supported_tests" in data
        assert len(data["supported_tests"]) > 0

    def test_invalid_data_handling(self):
        """測試無效資料處理"""
        payload = {
            "data": [],  # 空資料陣列
            "confidence_level": 0.95,
        }

        response = client.post("/statistics/descriptive", json=payload)
        assert response.status_code == 422  # 驗證錯誤
