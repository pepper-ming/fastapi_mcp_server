import pytest

from app.models.statistics import HypothesisTestRequest
from app.services.statistics import StatisticsService


class TestStatisticsService:
    """統計服務單元測試"""

    def test_descriptive_statistics_basic(self):
        """測試基本描述性統計計算"""
        data = [1, 2, 3, 4, 5]
        result = StatisticsService.calculate_descriptive_statistics(data)

        assert result.count == 5
        assert result.mean == 3.0
        assert result.median == 3.0
        assert abs(result.std_dev - 1.5811) < 0.001
        assert result.min_value == 1.0
        assert result.max_value == 5.0

    def test_descriptive_statistics_single_value(self):
        """測試單一數值的描述性統計"""
        data = [5.0]
        result = StatisticsService.calculate_descriptive_statistics(data)

        assert result.count == 1
        assert result.mean == 5.0
        assert result.median == 5.0
        assert result.std_dev == 0.0  # 單一值標準差為 0

    def test_hypothesis_test_one_sample_t(self):
        """測試單樣本 t 檢定"""
        # 已知結果的測試資料
        data = [2.1, 2.3, 1.9, 2.0, 2.2, 2.4, 1.8, 2.1, 2.0, 2.2]

        request = HypothesisTestRequest(
            sample_data=data,
            test_type="one_sample_t",
            null_hypothesis_value=2.0,
            alternative="two_sided",
            alpha=0.05,
        )

        result = StatisticsService.perform_hypothesis_test(request)

        assert isinstance(result.test_statistic, float)
        assert isinstance(result.p_value, float)
        assert 0 <= result.p_value <= 1
        assert result.degrees_of_freedom == 9
        assert isinstance(result.reject_null, bool)

    def test_hypothesis_test_invalid_type(self):
        """測試不支援的檢定類型"""
        request = HypothesisTestRequest(
            sample_data=[1, 2, 3], test_type="invalid_test", null_hypothesis_value=0
        )

        with pytest.raises(ValueError):
            StatisticsService.perform_hypothesis_test(request)
