from pydantic import BaseModel, Field


class StatisticalDataRequest(BaseModel):
    """統計資料請求模型"""

    data: list[int | float] = Field(
        ...,
        description="數值資料陣列",
        min_length=1,
        examples=[[1.2, 2.3, 3.4, 4.5, 5.6]],
    )

    confidence_level: float = Field(
        default=0.95, description="信賴水準", ge=0.01, le=0.99, examples=[0.95]
    )


class DescriptiveStatistics(BaseModel):
    """描述性統計結果模型"""

    count: int = Field(description="資料點數量")
    mean: float = Field(description="算術平均數")
    median: float = Field(description="中位數")
    mode: float | None = Field(description="眾數（如存在）")
    std_dev: float = Field(description="標準差")
    variance: float = Field(description="變異數")
    min_value: float = Field(description="最小值")
    max_value: float = Field(description="最大值")
    range_value: float = Field(description="全距")
    q1: float = Field(description="第一四分位數")
    q3: float = Field(description="第三四分位數")
    iqr: float = Field(description="四分位距")
    skewness: float = Field(description="偏度")
    kurtosis: float = Field(description="峰度")

    confidence_interval: dict[str, float] = Field(
        description="平均數信賴區間",
        examples=[{"lower": 2.5, "upper": 4.5, "level": 0.95}],
    )


class HypothesisTestRequest(BaseModel):
    """假設檢定請求模型"""

    sample_data: list[int | float] = Field(..., description="樣本資料", min_length=2)

    test_type: str = Field(
        default="one_sample_t", description="檢定類型", examples=["one_sample_t"]
    )

    null_hypothesis_value: float = Field(
        default=0.0, description="虛無假設數值", examples=[0.0]
    )

    alternative: str = Field(
        default="two_sided",
        description="對立假設類型：two_sided, greater, less",
        examples=["two_sided"],
    )

    alpha: float = Field(
        default=0.05, description="顯著水準", ge=0.001, le=0.1, examples=[0.05]
    )


class HypothesisTestResult(BaseModel):
    """假設檢定結果模型"""

    test_statistic: float = Field(description="檢定統計量")
    p_value: float = Field(description="p 值")
    critical_value: float | list[float] = Field(description="臨界值")
    degrees_of_freedom: int | None = Field(description="自由度")
    reject_null: bool = Field(description="是否拒絕虛無假設")
    conclusion: str = Field(description="檢定結論")
    effect_size: float | None = Field(description="效應量")
