from enum import Enum
from typing import Any, Optional, Union

from pydantic import BaseModel, Field


class CorrelationType(str, Enum):
    """相關性分析類型"""

    PEARSON = "pearson"
    SPEARMAN = "spearman"
    KENDALL = "kendall"


class RegressionType(str, Enum):
    """迴歸分析類型"""

    LINEAR = "linear"
    POLYNOMIAL = "polynomial"
    LOGISTIC = "logistic"
    RIDGE = "ridge"
    LASSO = "lasso"


class CorrelationRequest(BaseModel):
    """相關性分析請求"""

    x_data: list[Union[int, float]] = Field(..., description="X 變數資料", min_length=3)
    y_data: list[Union[int, float]] = Field(..., description="Y 變數資料", min_length=3)
    correlation_type: CorrelationType = Field(
        default=CorrelationType.PEARSON, description="相關性分析類型"
    )
    alpha: float = Field(default=0.05, ge=0.001, le=0.1, description="顯著水準")


class CorrelationResult(BaseModel):
    """相關性分析結果"""

    correlation_coefficient: float = Field(description="相關係數")
    p_value: float = Field(description="p 值")
    confidence_interval: dict[str, Optional[float]] = Field(description="信賴區間")
    interpretation: str = Field(description="結果詮釋")
    strength: str = Field(description="相關強度")


class RegressionRequest(BaseModel):
    """迴歸分析請求"""

    x_data: list[Union[int, float]] = Field(..., description="自變數資料", min_length=3)
    y_data: list[Union[int, float]] = Field(..., description="依變數資料", min_length=3)
    regression_type: RegressionType = Field(
        default=RegressionType.LINEAR, description="迴歸類型"
    )
    polynomial_degree: Optional[int] = Field(
        default=2, ge=2, le=5, description="多項式次數"
    )
    alpha: float = Field(default=0.05, description="正則化參數 (Ridge/Lasso)")


class RegressionResult(BaseModel):
    """迴歸分析結果"""

    coefficients: list[float] = Field(description="迴歸係數")
    intercept: float = Field(description="截距")
    r_squared: float = Field(description="決定係數")
    adjusted_r_squared: float = Field(description="調整後決定係數")
    f_statistic: float = Field(description="F 統計量")
    f_p_value: float = Field(description="F 檢定 p 值")
    residual_analysis: dict[str, Any] = Field(description="殘差分析")
    prediction_equation: str = Field(description="預測方程式")
