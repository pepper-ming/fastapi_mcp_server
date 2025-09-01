import numpy as np
from scipy import stats

from app.models.statistics import (
    DescriptiveStatistics,
    HypothesisTestRequest,
    HypothesisTestResult,
)


class StatisticsService:
    """統計分析服務類別"""

    @staticmethod
    def calculate_descriptive_statistics(
        data: list[int | float], confidence_level: float = 0.95
    ) -> DescriptiveStatistics:
        """計算描述性統計"""

        np_data = np.array(data)
        n = len(np_data)

        # 基本統計量
        mean_val = float(np.mean(np_data))
        median_val = float(np.median(np_data))
        std_val = float(np.std(np_data, ddof=1))  # 樣本標準差
        var_val = float(np.var(np_data, ddof=1))  # 樣本變異數

        # 分位數
        q1 = float(np.percentile(np_data, 25))
        q3 = float(np.percentile(np_data, 75))

        # 眾數（可能不存在）
        mode_result = stats.mode(np_data, keepdims=False)
        mode_val = float(mode_result.mode) if mode_result.count > 1 else None

        # 形狀統計量
        skew_val = float(stats.skew(np_data))
        kurtosis_val = float(stats.kurtosis(np_data))

        # 信賴區間
        alpha = 1 - confidence_level
        t_critical = stats.t.ppf(1 - alpha / 2, df=n - 1)
        margin_error = t_critical * (std_val / np.sqrt(n))
        ci_lower = mean_val - margin_error
        ci_upper = mean_val + margin_error

        return DescriptiveStatistics(
            count=n,
            mean=mean_val,
            median=median_val,
            mode=mode_val,
            std_dev=std_val,
            variance=var_val,
            min_value=float(np.min(np_data)),
            max_value=float(np.max(np_data)),
            range_value=float(np.ptp(np_data)),
            q1=q1,
            q3=q3,
            iqr=q3 - q1,
            skewness=skew_val,
            kurtosis=kurtosis_val,
            confidence_interval={
                "lower": ci_lower,
                "upper": ci_upper,
                "level": confidence_level,
            },
        )

    @staticmethod
    def perform_hypothesis_test(request: HypothesisTestRequest) -> HypothesisTestResult:
        """執行假設檢定"""

        data = np.array(request.sample_data)

        if request.test_type == "one_sample_t":
            # 單樣本 t 檢定
            t_stat, p_value = stats.ttest_1samp(
                data, request.null_hypothesis_value, alternative=request.alternative
            )

            df = len(data) - 1
            alpha = request.alpha

            if request.alternative == "two_sided":
                critical_value = [
                    -stats.t.ppf(1 - alpha / 2, df),
                    stats.t.ppf(1 - alpha / 2, df),
                ]
            elif request.alternative == "greater":
                critical_value = stats.t.ppf(1 - alpha, df)
            else:  # less
                critical_value = -stats.t.ppf(1 - alpha, df)

            # Cohen's d 效應量
            mean_diff = np.mean(data) - request.null_hypothesis_value
            effect_size = mean_diff / np.std(data, ddof=1)

            reject_null = p_value < alpha

            if reject_null:
                conclusion = f"在 α = {alpha} 水準下拒絕虛無假設"
            else:
                conclusion = f"在 α = {alpha} 水準下不拒絕虛無假設"

            return HypothesisTestResult(
                test_statistic=float(t_stat),
                p_value=float(p_value),
                critical_value=critical_value,
                degrees_of_freedom=df,
                reject_null=reject_null,
                conclusion=conclusion,
                effect_size=float(effect_size),
            )

        else:
            raise ValueError(f"不支援的檢定類型: {request.test_type}")
