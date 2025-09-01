import numpy as np
from scipy import stats
from sklearn.linear_model import Lasso, LinearRegression, LogisticRegression, Ridge
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import PolynomialFeatures

from app.models.advanced_statistics import (
    CorrelationRequest,
    CorrelationResult,
    CorrelationType,
    RegressionRequest,
    RegressionResult,
    RegressionType,
)


class AdvancedStatisticsService:
    """進階統計分析服務"""

    @staticmethod
    def calculate_correlation(request: CorrelationRequest) -> CorrelationResult:
        """計算相關性分析"""

        x = np.array(request.x_data)
        y = np.array(request.y_data)

        if len(x) != len(y):
            raise ValueError("X 和 Y 資料長度必須相同")

        # 計算相關係數
        if request.correlation_type == CorrelationType.PEARSON:
            corr_coef, p_value = stats.pearsonr(x, y)
            method_name = "Pearson"
        elif request.correlation_type == CorrelationType.SPEARMAN:
            corr_coef, p_value = stats.spearmanr(x, y)
            method_name = "Spearman"
        elif request.correlation_type == CorrelationType.KENDALL:
            corr_coef, p_value = stats.kendalltau(x, y)
            method_name = "Kendall"
        else:
            raise ValueError(f"不支援的相關性分析類型: {request.correlation_type}")

        # 計算信賴區間 (僅適用於 Pearson)
        if request.correlation_type == CorrelationType.PEARSON:
            n = len(x)
            z_score = stats.norm.ppf(1 - request.alpha / 2)
            se = 1 / np.sqrt(n - 3)
            z_r = 0.5 * np.log((1 + corr_coef) / (1 - corr_coef))
            ci_lower = np.tanh(z_r - z_score * se)
            ci_upper = np.tanh(z_r + z_score * se)
        else:
            ci_lower, ci_upper = None, None

        # 判定相關強度
        abs_corr = abs(corr_coef)
        if abs_corr < 0.3:
            strength = "弱相關"
        elif abs_corr < 0.7:
            strength = "中等相關"
        else:
            strength = "強相關"

        # 結果詮釋
        direction = "正" if corr_coef > 0 else "負"
        significance = "顯著" if p_value < request.alpha else "不顯著"
        interpretation = f"{method_name} 相關性分析顯示 {direction}相關 (r = {corr_coef:.4f})，在 α = {request.alpha} 水準下{significance}"

        return CorrelationResult(
            correlation_coefficient=float(corr_coef),
            p_value=float(p_value),
            confidence_interval={
                "lower": float(ci_lower) if ci_lower is not None else None,
                "upper": float(ci_upper) if ci_upper is not None else None,
                "level": 1 - request.alpha,
            },
            interpretation=interpretation,
            strength=strength,
        )

    @staticmethod
    def perform_regression(request: RegressionRequest) -> RegressionResult:
        """執行迴歸分析"""

        x = np.array(request.x_data).reshape(-1, 1)
        y = np.array(request.y_data)

        if len(x) != len(y):
            raise ValueError("X 和 Y 資料長度必須相同")

        # 選擇迴歸模型
        if request.regression_type == RegressionType.LINEAR:
            model = LinearRegression()
            x_processed = x

        elif request.regression_type == RegressionType.POLYNOMIAL:
            poly_features = PolynomialFeatures(degree=request.polynomial_degree)
            x_processed = poly_features.fit_transform(x)
            model = LinearRegression()

        elif request.regression_type == RegressionType.RIDGE:
            model = Ridge(alpha=request.alpha)
            x_processed = x

        elif request.regression_type == RegressionType.LASSO:
            model = Lasso(alpha=request.alpha)
            x_processed = x

        elif request.regression_type == RegressionType.LOGISTIC:
            model = LogisticRegression()
            x_processed = x
        else:
            raise ValueError(f"不支援的迴歸類型: {request.regression_type}")

        # 訓練模型
        model.fit(x_processed, y)

        # 預測
        y_pred = model.predict(x_processed)

        # 計算統計量
        if request.regression_type != RegressionType.LOGISTIC:
            # 使用 sklearn.metrics.r2_score 計算 R²
            r2 = r2_score(y, y_pred)
            n = len(y)
            p = x_processed.shape[1]  # 參數個數
            adjusted_r2 = 1 - (1 - r2) * (n - 1) / (n - p - 1)

            # F 統計量
            mse_model = mean_squared_error(y, y_pred)
            mse_total = np.var(y)
            if mse_model > 1e-10 and mse_total > 1e-10:  # 避免除以零
                f_stat = ((mse_total - mse_model) / p) / (mse_model / (n - p - 1))
                f_p_value = 1 - stats.f.cdf(f_stat, p, n - p - 1)
            else:
                # 完美預測的情況
                f_stat = 999999.0  # 使用大數值而非 infinity
                f_p_value = 0.0
        else:
            # 邏輯迴歸使用不同的評估指標
            r2 = model.score(x_processed, y)
            adjusted_r2 = r2  # 簡化處理
            f_stat = 0.0
            f_p_value = 1.0

        # 殘差分析
        if request.regression_type != RegressionType.LOGISTIC:
            residuals = y - y_pred
            residual_analysis = {
                "mean_residual": float(np.mean(residuals)),
                "std_residual": float(np.std(residuals)),
                "shapiro_wilk_p": float(stats.shapiro(residuals)[1]),
                "durbin_watson": float(
                    AdvancedStatisticsService._durbin_watson(residuals)
                ),
            }
        else:
            residual_analysis = {"note": "邏輯迴歸不適用殘差分析"}

        # 預測方程式
        if hasattr(model, "coef_"):
            coef = model.coef_
            intercept = model.intercept_

            if request.regression_type == RegressionType.LINEAR:
                equation = f"Y = {intercept:.4f} + {coef[0]:.4f} * X"
            elif request.regression_type == RegressionType.POLYNOMIAL:
                terms = [f"{intercept:.4f}"]
                for i, c in enumerate(coef):
                    if i == 0:
                        terms.append(f"{c:.4f} * X")
                    else:
                        terms.append(f"{c:.4f} * X^{i+1}")
                equation = "Y = " + " + ".join(terms)
            else:
                equation = f"Y = {intercept:.4f} + {coef[0]:.4f} * X"
        else:
            coef = np.array([])
            intercept = 0.0
            equation = "方程式不可用"

        return RegressionResult(
            coefficients=coef.tolist() if len(coef.shape) > 0 else [],
            intercept=float(intercept),
            r_squared=float(r2),
            adjusted_r_squared=float(adjusted_r2),
            f_statistic=float(f_stat),
            f_p_value=float(f_p_value),
            residual_analysis=residual_analysis,
            prediction_equation=equation,
        )

    @staticmethod
    def _durbin_watson(residuals: np.ndarray) -> float:
        """計算 Durbin-Watson 統計量"""
        diff = np.diff(residuals)
        sum_residuals_sq = np.sum(residuals**2)
        if sum_residuals_sq > 1e-10:  # 避免除以零
            return np.sum(diff**2) / sum_residuals_sq
        else:
            return 2.0  # DW 統計量在完美預測時接近 2
