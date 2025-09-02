import numpy as np
import pandas as pd
from scipy import stats
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error

from app.models.timeseries import (
    AnomalyDetectionRequest,
    AnomalyDetectionResult,
    AnomalyPoint,
    ForecastModel,
    ForecastRequest,
    ForecastResult,
    TimeSeriesData,
)
from app.utils.cache_decorators import cache_forecast_result


class TimeSeriesService:
    """時間序列分析服務"""

    @staticmethod
    @cache_forecast_result(ttl_seconds=1800)
    def forecast_timeseries(request: ForecastRequest) -> ForecastResult:
        """時間序列預測"""

        # 準備資料
        df = TimeSeriesService._prepare_dataframe(request.timeseries)

        if request.model_type == ForecastModel.LINEAR_TREND:
            return TimeSeriesService._linear_trend_forecast(request, df)
        elif request.model_type == ForecastModel.MOVING_AVERAGE:
            return TimeSeriesService._moving_average_forecast(request, df)
        elif request.model_type == ForecastModel.EXPONENTIAL_SMOOTHING:
            return TimeSeriesService._exponential_smoothing_forecast(request, df)
        elif request.model_type == ForecastModel.ARIMA:
            return TimeSeriesService._arima_forecast(request, df)
        else:
            raise ValueError(f"不支援的預測模型: {request.model_type}")

    @staticmethod
    def detect_anomalies(request: AnomalyDetectionRequest) -> AnomalyDetectionResult:
        """異常檢測"""

        df = TimeSeriesService._prepare_dataframe(request.timeseries)

        if request.detection_method == "statistical":
            anomalies = TimeSeriesService._statistical_anomaly_detection(
                df, request.sensitivity
            )
        elif request.detection_method == "iqr":
            anomalies = TimeSeriesService._iqr_anomaly_detection(
                df, request.sensitivity
            )
        elif request.detection_method == "zscore":
            anomalies = TimeSeriesService._zscore_anomaly_detection(
                df, request.sensitivity
            )
        else:
            raise ValueError(f"不支援的異常檢測方法: {request.detection_method}")

        anomaly_rate = len(anomalies) / len(df) if len(df) > 0 else 0

        return AnomalyDetectionResult(
            series_id=request.timeseries.series_id,
            detection_method=request.detection_method,
            anomaly_points=anomalies,
            anomaly_rate=anomaly_rate,
            summary=f"使用 {request.detection_method} 方法檢測到 {len(anomalies)} 個異常點，異常率為 {anomaly_rate:.2%}",
        )

    @staticmethod
    def _prepare_dataframe(timeseries: TimeSeriesData) -> pd.DataFrame:
        """準備 pandas DataFrame"""
        data = []
        for point in timeseries.data:
            data.append({"timestamp": point.timestamp, "value": point.value})

        df = pd.DataFrame(data)
        df = df.sort_values("timestamp")
        df = df.reset_index(drop=True)
        return df

    @staticmethod
    def _linear_trend_forecast(
        request: ForecastRequest, df: pd.DataFrame
    ) -> ForecastResult:
        """線性趨勢預測"""

        # 準備特徵 (時間轉換為數值)
        df["time_numeric"] = pd.to_numeric(df["timestamp"])
        X = df["time_numeric"].values.reshape(-1, 1)
        y = df["value"].values

        # 訓練線性回歸模型
        model = LinearRegression()
        model.fit(X, y)

        # 生成預測時間點
        last_time = df["timestamp"].iloc[-1]
        time_diff = df["timestamp"].iloc[-1] - df["timestamp"].iloc[-2]
        forecast_dates = []
        for i in range(1, request.forecast_periods + 1):
            forecast_dates.append(last_time + i * time_diff)

        # 預測
        forecast_times_numeric = pd.to_numeric(
            pd.Series(forecast_dates)
        ).values.reshape(-1, 1)
        forecast_values = model.predict(forecast_times_numeric)

        # 計算信賴區間
        y_pred = model.predict(X)
        mse = mean_squared_error(y, y_pred)
        std_error = np.sqrt(mse)

        z_score = stats.norm.ppf(1 - (1 - request.confidence_level) / 2)
        confidence_intervals = []
        for val in forecast_values:
            confidence_intervals.append(
                {"lower": val - z_score * std_error, "upper": val + z_score * std_error}
            )

        # 模型評估
        mae = mean_absolute_error(y, y_pred)
        r2 = model.score(X, y)

        return ForecastResult(
            series_id=request.timeseries.series_id,
            model_type="linear_trend",
            forecast_values=forecast_values.tolist(),
            forecast_dates=forecast_dates,
            confidence_intervals=confidence_intervals,
            model_metrics={"mae": mae, "mse": mse, "r2": r2, "rmse": np.sqrt(mse)},
            model_summary=f"線性趨勢模型 (R² = {r2:.4f}, RMSE = {np.sqrt(mse):.4f})",
        )

    @staticmethod
    def _moving_average_forecast(
        request: ForecastRequest, df: pd.DataFrame
    ) -> ForecastResult:
        """移動平均預測"""

        values = df["value"].values
        window = request.ma_window

        # 計算移動平均
        if len(values) < window:
            raise ValueError(f"資料點數量 ({len(values)}) 少於移動平均視窗 ({window})")

        # 最近 window 個點的平均值作為預測值
        recent_values = values[-window:]
        forecast_value = np.mean(recent_values)

        # 生成預測時間點和值
        last_time = df["timestamp"].iloc[-1]
        time_diff = df["timestamp"].iloc[-1] - df["timestamp"].iloc[-2]
        forecast_dates = []
        forecast_values = []

        for i in range(1, request.forecast_periods + 1):
            forecast_dates.append(last_time + i * time_diff)
            forecast_values.append(forecast_value)  # 簡化處理：所有預測值相同

        # 計算標準誤差
        std_error = np.std(recent_values)
        z_score = stats.norm.ppf(1 - (1 - request.confidence_level) / 2)

        confidence_intervals = []
        for val in forecast_values:
            confidence_intervals.append(
                {"lower": val - z_score * std_error, "upper": val + z_score * std_error}
            )

        return ForecastResult(
            series_id=request.timeseries.series_id,
            model_type="moving_average",
            forecast_values=forecast_values,
            forecast_dates=forecast_dates,
            confidence_intervals=confidence_intervals,
            model_metrics={"window_size": window, "forecast_std": std_error},
            model_summary=f"{window} 期移動平均預測",
        )

    @staticmethod
    def _exponential_smoothing_forecast(
        request: ForecastRequest, df: pd.DataFrame
    ) -> ForecastResult:
        """指數平滑預測"""

        values = df["value"].values
        alpha = 0.3  # 平滑參數

        # 簡單指數平滑
        smoothed = [values[0]]
        for i in range(1, len(values)):
            smoothed.append(alpha * values[i] + (1 - alpha) * smoothed[-1])

        # 預測值為最後一個平滑值
        forecast_value = smoothed[-1]

        # 生成預測時間點和值
        last_time = df["timestamp"].iloc[-1]
        time_diff = df["timestamp"].iloc[-1] - df["timestamp"].iloc[-2]
        forecast_dates = []
        forecast_values = []

        for i in range(1, request.forecast_periods + 1):
            forecast_dates.append(last_time + i * time_diff)
            forecast_values.append(forecast_value)

        # 計算殘差標準差
        residuals = values[1:] - smoothed[:-1]
        std_error = np.std(residuals)
        z_score = stats.norm.ppf(1 - (1 - request.confidence_level) / 2)

        confidence_intervals = []
        for val in forecast_values:
            confidence_intervals.append(
                {"lower": val - z_score * std_error, "upper": val + z_score * std_error}
            )

        return ForecastResult(
            series_id=request.timeseries.series_id,
            model_type="exponential_smoothing",
            forecast_values=forecast_values,
            forecast_dates=forecast_dates,
            confidence_intervals=confidence_intervals,
            model_metrics={"alpha": alpha, "residual_std": std_error},
            model_summary=f"指數平滑預測 (α = {alpha})",
        )

    @staticmethod
    def _arima_forecast(request: ForecastRequest, df: pd.DataFrame) -> ForecastResult:
        """ARIMA 預測 (簡化版本)"""
        # 注意：這是一個簡化的 ARIMA 實作
        # 在實際應用中建議使用 statsmodels 或 pmdarima

        values = df["value"].values

        # 簡化處理：使用一階差分和移動平均
        if len(values) < 10:
            raise ValueError("ARIMA 模型需要至少 10 個資料點")

        # 一階差分
        diff_values = np.diff(values)

        # 預測差分值 (使用最近 3 個差分值的平均)
        recent_diffs = diff_values[-3:]
        forecast_diff = np.mean(recent_diffs)

        # 生成預測
        last_value = values[-1]
        forecast_values = []
        current_value = last_value

        for _ in range(request.forecast_periods):
            current_value = current_value + forecast_diff
            forecast_values.append(current_value)

        # 生成預測時間點
        last_time = df["timestamp"].iloc[-1]
        time_diff = df["timestamp"].iloc[-1] - df["timestamp"].iloc[-2]
        forecast_dates = []

        for i in range(1, request.forecast_periods + 1):
            forecast_dates.append(last_time + i * time_diff)

        # 簡化的信賴區間
        std_error = np.std(diff_values)
        z_score = stats.norm.ppf(1 - (1 - request.confidence_level) / 2)

        confidence_intervals = []
        for i, val in enumerate(forecast_values):
            # 誤差隨預測期增加而增大
            adjusted_std = std_error * np.sqrt(i + 1)
            confidence_intervals.append(
                {
                    "lower": val - z_score * adjusted_std,
                    "upper": val + z_score * adjusted_std,
                }
            )

        return ForecastResult(
            series_id=request.timeseries.series_id,
            model_type="arima",
            forecast_values=forecast_values,
            forecast_dates=forecast_dates,
            confidence_intervals=confidence_intervals,
            model_metrics={"order": request.arima_order, "diff_std": std_error},
            model_summary=f"ARIMA{request.arima_order} 預測 (簡化版本)",
        )

    @staticmethod
    def _statistical_anomaly_detection(
        df: pd.DataFrame, sensitivity: float
    ) -> list[AnomalyPoint]:
        """統計方法異常檢測"""
        values = df["value"].values
        mean_val = np.mean(values)
        std_val = np.std(values)

        threshold = sensitivity * std_val
        anomalies = []

        for i, (_, row) in enumerate(df.iterrows()):
            deviation = abs(row["value"] - mean_val)
            if deviation > threshold:
                anomalies.append(
                    AnomalyPoint(
                        timestamp=row["timestamp"],
                        value=row["value"],
                        anomaly_score=deviation / std_val,
                        expected_range={
                            "lower": mean_val - threshold,
                            "upper": mean_val + threshold,
                        },
                    )
                )

        return anomalies

    @staticmethod
    def _iqr_anomaly_detection(
        df: pd.DataFrame, sensitivity: float
    ) -> list[AnomalyPoint]:
        """IQR 方法異常檢測"""
        values = df["value"].values
        q1 = np.percentile(values, 25)
        q3 = np.percentile(values, 75)
        iqr = q3 - q1

        lower_bound = q1 - sensitivity * iqr
        upper_bound = q3 + sensitivity * iqr

        anomalies = []
        for _, row in df.iterrows():
            if row["value"] < lower_bound or row["value"] > upper_bound:
                anomalies.append(
                    AnomalyPoint(
                        timestamp=row["timestamp"],
                        value=row["value"],
                        anomaly_score=abs(row["value"] - (q1 + q3) / 2) / iqr,
                        expected_range={"lower": lower_bound, "upper": upper_bound},
                    )
                )

        return anomalies

    @staticmethod
    def _zscore_anomaly_detection(
        df: pd.DataFrame, sensitivity: float
    ) -> list[AnomalyPoint]:
        """Z-score 方法異常檢測"""
        values = df["value"].values
        z_scores = np.abs(stats.zscore(values))

        anomalies = []
        for i, (_, row) in enumerate(df.iterrows()):
            if z_scores[i] > sensitivity:
                anomalies.append(
                    AnomalyPoint(
                        timestamp=row["timestamp"],
                        value=row["value"],
                        anomaly_score=z_scores[i],
                        expected_range={
                            "lower": np.mean(values) - sensitivity * np.std(values),
                            "upper": np.mean(values) + sensitivity * np.std(values),
                        },
                    )
                )

        return anomalies
