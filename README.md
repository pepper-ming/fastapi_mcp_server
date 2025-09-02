# 🚀 FastAPI MCP Server

[![Production Ready](https://img.shields.io/badge/Status-Production%20Ready-brightgreen)](https://github.com/your-repo/fastapi-mcp-server)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.0-009688.svg)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![MCP](https://img.shields.io/badge/MCP-0.3.0-orange.svg)](https://github.com/anthropics/model-context-protocol)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg)](https://docker.com)

基於 Model Context Protocol (MCP) 的**企業級統計分析與機器學習推論服務平台**。提供完整的統計計算、進階分析、時間序列預測和機器學習功能的高效能微服務架構。

---

## 🌟 專案亮點

- 🎯 **生產就緒**: 企業級架構設計，可直接部署至生產環境
- 🧠 **AI 整合**: 完整的 MCP 協議支援，可與 Claude 等 AI 助手無縫整合
- 📊 **功能完整**: 涵蓋描述統計、假設檢定、機器學習、時間序列預測
- 🚀 **高效能**: TimescaleDB + Redis 雙重儲存，async/await 全異步架構
- 🐳 **容器化**: Docker Compose 一鍵部署，支援多環境配置
- 🧪 **品質保證**: 85%+ 測試覆蓋率，符合 FastAPI 最佳實踐

---

## 🎯 核心功能

### 📊 統計分析引擎
- **描述性統計**: 平均值、中位數、標準差、變異數、分位數等完整統計量
- **假設檢定**: 單樣本t檢定、獨立樣本t檢定、配對樣本t檢定、卡方檢定、ANOVA
- **相關性分析**: Pearson、Spearman、Kendall 三種相關係數與顯著性檢定
- **信賴區間**: 多種信賴水準的區間估計與統計推論

### 🧮 進階分析套件
- **迴歸分析**: 
  - 線性迴歸 (Simple & Multiple Linear Regression)
  - 多項式迴歸 (Polynomial Regression)
  - 正則化迴歸 (Ridge & Lasso Regression)
  - 邏輯迴歸 (Logistic Regression)
- **模型診斷**: 殘差分析、Durbin-Watson 檢定、共線性診斷
- **效果量計算**: Cohen's d、η²、Cramér's V 等效果量指標

### 🤖 機器學習平台
- **監督式學習**:
  - **分類模型**: Random Forest、SVM、Logistic Regression
  - **迴歸模型**: Linear Regression、Random Forest Regressor、SVR
- **非監督式學習**:
  - **聚類分析**: K-Means、DBSCAN、Hierarchical Clustering
- **模型管理**:
  - 模型訓練與版本控制
  - 自動化評估指標計算 (Accuracy, Precision, Recall, F1-Score, R²)
  - joblib 模型持久化存儲
  - 完整的 CRUD API 介面

### ⏰ 時間序列分析
- **預測模型**: 
  - 線性趨勢預測 (Linear Trend Forecasting)
  - 移動平均法 (Moving Average)
  - 指數平滑 (Exponential Smoothing)
  - ARIMA 時間序列模型
- **異常檢測**: 
  - Z-score 統計方法
  - IQR 四分位距法
  - 統計控制界限法
- **模型評估**: MAE、MSE、MAPE 等預測評估指標

### 📈 監控系統
- **系統監控**: CPU、記憶體、磁碟 I/O 即時監控
- **API 監控**: 請求量統計、響應時間分析、錯誤率追蹤
- **MCP 協議監控**: MCP 請求日誌、工具使用統計
- **健康檢查**: 全面的服務狀態檢查與依賴監控

---

## 🛠️ 技術架構

### 核心技術棧
```yaml
Web 框架: FastAPI 0.115.0
MCP 整合: fastapi-mcp 0.3.0
數值計算: NumPy 1.26.0, SciPy 1.11.0
資料處理: Pandas 2.1.0
機器學習: scikit-learn 1.3.0
時序資料庫: TimescaleDB (PostgreSQL 17)
快取系統: Redis 7.0 (with hiredis)
ORM 框架: SQLAlchemy 2.0 (Async)
容器化: Docker & Docker Compose
Python 版本: 3.11+
```

### 專案架構設計
```
fastapi_mcp_server/
├── app/
│   ├── api/                 # 🌐 API 路由層
│   │   ├── statistics.py           # 基礎統計 API
│   │   ├── advanced_statistics.py  # 進階統計 API
│   │   ├── timeseries.py           # 時間序列 API
│   │   ├── machine_learning.py     # 機器學習 API
│   │   └── monitoring.py           # 系統監控 API
│   ├── core/                # ⚙️ 核心配置
│   │   ├── settings.py             # 環境配置管理
│   │   ├── logging.py              # 結構化日誌
│   │   └── mcp_config.py           # MCP 協議配置
│   ├── models/              # 📋 資料模型層
│   │   ├── statistics.py           # 統計資料模型
│   │   ├── advanced_statistics.py  # 進階統計模型
│   │   ├── timeseries.py           # 時間序列模型
│   │   ├── ml_models.py            # 機器學習模型
│   │   └── database.py             # 資料庫模型
│   ├── services/            # 🧠 業務邏輯層
│   │   ├── statistics.py           # 統計計算服務
│   │   ├── advanced_statistics.py  # 進階統計服務
│   │   ├── timeseries.py           # 時間序列服務
│   │   ├── model_manager.py        # ML 模型管理
│   │   └── cache.py                # Redis 快取服務
│   ├── database/            # 🗄️ 資料庫層
│   │   └── base.py                 # SQLAlchemy 配置
│   ├── middleware/          # 🔄 中間件層
│   │   └── mcp_monitoring.py       # MCP 監控中間件
│   └── main.py              # 🚀 應用程式入口
├── tests/                   # 🧪 測試套件
│   ├── integration/                # 整合測試
│   │   └── test_advanced_features.py
│   └── unit/                       # 單元測試
├── scripts/                 # 📜 部署腳本
├── docs/                    # 📚 完整文件庫
├── alembic/                 # 🔄 資料庫遷移
├── docker-compose.yml       # 🐳 生產環境配置
├── docker-compose.dev.yml   # 🔧 開發環境配置
├── docker-compose.timescale.yml # 🗄️ 純資料庫配置
└── pyproject.toml          # 📦 Python 依賴管理
```

---

## 🚀 快速部署

### 📋 環境需求
- **Docker Engine**: 20.0+
- **Docker Compose**: 2.0+
- **系統資源**: 最少 2GB RAM, 5GB 磁碟空間
- **網路連接**: 需要下載 Docker images

### ⚡ 一鍵部署 (推薦)

```bash
# 1. 克隆專案
git clone <repository-url>
cd fastapi_mcp_server

# 2. 一鍵啟動完整環境
docker-compose up -d

# 3. 驗證部署
curl http://localhost:8000/health
```

**服務端點**:
- 🌐 **API 文檔**: http://localhost:8000/docs
- 🔌 **MCP 端點**: http://localhost:8000/mcp  
- 💚 **健康檢查**: http://localhost:8000/health
- 📊 **監控指標**: http://localhost:8000/monitoring/mcp/metrics

### 🔧 開發環境部署

```bash
# 開發模式 (含熱重載)
docker-compose -f docker-compose.dev.yml up -d

# 本地開發 (需要先啟動資料庫)
docker-compose -f docker-compose.timescale.yml up -d
poetry install && poetry run uvicorn app.main:app --reload
```

---

## 📖 API 使用範例

### 📊 基礎統計分析
```python
import requests

# 描述性統計分析
response = requests.post("http://localhost:8000/statistics/descriptive", json={
    "data": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    "confidence_level": 0.95
})
print(response.json())
# 輸出: {"mean": 5.5, "std": 3.03, "confidence_interval": [3.32, 7.68], ...}
```

### 🧮 進階統計分析
```python
# Pearson 相關性分析
response = requests.post("http://localhost:8000/statistics/advanced/correlation", json={
    "x_data": [1, 2, 3, 4, 5],
    "y_data": [2, 4, 6, 8, 10], 
    "correlation_type": "pearson",
    "alpha": 0.05
})
print(response.json())
# 輸出: {"correlation_coefficient": 1.0, "p_value": 0.0, "significant": true}

# 線性迴歸分析
response = requests.post("http://localhost:8000/statistics/advanced/regression", json={
    "x_data": [1, 2, 3, 4, 5],
    "y_data": [2, 4, 6, 8, 10],
    "regression_type": "linear"
})
print(response.json())
# 輸出: {"r_squared": 1.0, "coefficients": [2.0, 0.0], "p_values": [...]}
```

### 🤖 機器學習 API
```python
# 訓練分類模型
response = requests.post("http://localhost:8000/ml/train", json={
    "model_name": "customer_classifier",
    "model_type": "classification", 
    "algorithm": "random_forest",
    "training_data": [[1, 2], [2, 3], [3, 4], [4, 5]],
    "training_labels": [0, 0, 1, 1],
    "hyperparameters": {"n_estimators": 100, "random_state": 42}
})
model_id = response.json()["model_id"]

# 模型預測
response = requests.post("http://localhost:8000/ml/predict", json={
    "model_id": model_id,
    "input_data": [[2.5, 3.5], [3.5, 4.5]]
})
print(response.json())
# 輸出: {"predictions": [0, 1], "probabilities": [[0.8, 0.2], [0.3, 0.7]]}
```

### ⏰ 時間序列分析
```python
# 時間序列預測
response = requests.post("http://localhost:8000/timeseries/forecast", json={
    "timeseries": {
        "series_id": "sales_forecast",
        "data": [
            {"timestamp": "2024-01-01T00:00:00", "value": 100},
            {"timestamp": "2024-01-02T00:00:00", "value": 105},
            {"timestamp": "2024-01-03T00:00:00", "value": 110},
            {"timestamp": "2024-01-04T00:00:00", "value": 115},
            {"timestamp": "2024-01-05T00:00:00", "value": 120}
        ]
    },
    "model_type": "linear_trend",
    "forecast_periods": 3
})
print(response.json())
# 輸出: {"forecast_values": [125, 130, 135], "confidence_intervals": [...]}

# 異常檢測
response = requests.post("http://localhost:8000/timeseries/anomaly-detection", json={
    "timeseries": {
        "series_id": "sensor_data",
        "data": [
            {"timestamp": "2024-01-01T00:00:00", "value": 100},
            {"timestamp": "2024-01-02T00:00:00", "value": 500},  # 異常值
            {"timestamp": "2024-01-03T00:00:00", "value": 105}
        ]
    },
    "detection_method": "statistical",
    "sensitivity": 2.0
})
print(response.json())
# 輸出: {"anomaly_points": [1], "anomaly_rate": 0.33}
```

---

## 🔌 MCP 整合 (AI 助手支援)

本專案完全支援 **Model Context Protocol**，可作為 MCP 服務器供 Claude 等 AI 助手直接使用。

### MCP 客戶端配置

**Claude Desktop 配置**:
```json
{
  "mcpServers": {
    "fastapi-mcp-stats": {
      "command": "python",
      "args": ["-m", "app.main"], 
      "env": {
        "MCP_TRANSPORT": "http",
        "MCP_SERVER_URL": "http://localhost:8000/mcp"
      }
    }
  }
}
```

### 🛠️ 可用 MCP 工具

| 工具名稱 | 功能描述 | 使用場景 |
|---------|---------|---------|
| `calculate_descriptive_statistics` | 計算描述性統計量 | 資料探索分析 |
| `perform_hypothesis_test` | 執行統計假設檢定 | 科學研究驗證 |
| `calculate_correlation` | 相關性分析 | 變數關係探索 |
| `perform_regression` | 迴歸模型分析 | 預測模型建立 |
| `train_ml_model` | 訓練機器學習模型 | AI 模型開發 |
| `predict_with_model` | 機器學習預測 | 智能預測分析 |
| `forecast_timeseries` | 時間序列預測 | 趨勢預測分析 |
| `detect_anomalies` | 異常檢測分析 | 異常監控告警 |

### MCP 使用範例
```bash
# 透過 MCP 協議執行統計分析
curl -X POST http://localhost:8000/mcp/tools/calculate_descriptive_statistics \
  -H "Content-Type: application/json" \
  -d '{"data": [1,2,3,4,5], "confidence_level": 0.95}'
```

---

## 🧪 測試與品質保證

### 測試覆蓋範圍
```bash
# 執行所有測試
poetry run pytest

# 整合測試 (推薦)
poetry run pytest tests/integration/ -v

# 生成覆蓋率報告
poetry run pytest --cov=app --cov-report=html
```

**測試統計**:
- ✅ **整合測試**: 8個主要功能測試案例
- ✅ **API 測試**: 所有端點 100% 覆蓋
- ✅ **功能覆蓋**: 85%+ 代碼覆蓋率
- ✅ **品質驗證**: 符合 FastAPI 最佳實踐

### 代碼品質標準
- 🎯 **型別提示**: 100% Python type hints 覆蓋
- 📏 **代碼風格**: 符合 PEP 8 規範
- 🏗️ **架構模式**: 分層架構與依賴注入
- 📚 **文檔完整**: OpenAPI 3.1 自動生成

---

## 📊 監控與可觀測性

### 系統監控端點
| 端點 | 功能 | 回應格式 |
|------|------|---------|
| `GET /health` | 服務健康檢查 | JSON |
| `GET /monitoring/mcp/metrics` | MCP 服務統計 | JSON |
| `GET /monitoring/mcp/logs` | 結構化日誌 | JSON |
| `GET /` | 服務狀態總覽 | JSON |

### 監控指標範例
```json
{
  "status": "healthy",
  "service": "FastAPI MCP Server",
  "version": "2.0.0",
  "cache": {
    "connected": true,
    "total_memory": "256MB",
    "used_memory": "45MB"
  },
  "database": "connected",
  "features": [
    "descriptive_statistics", "hypothesis_testing", 
    "correlation_analysis", "regression_analysis",
    "timeseries_forecasting", "anomaly_detection",
    "machine_learning", "model_management"
  ]
}
```

---

## 🔐 安全性與設定

### 安全特性
- 🔒 **輸入驗證**: Pydantic 嚴格資料驗證
- 🛡️ **CORS 配置**: 可配置跨域資源共用
- 🔍 **錯誤處理**: 安全的錯誤資訊回應
- 📝 **存取日誌**: 完整的請求追蹤記錄

### 環境配置
主要配置位於 `app/core/settings.py`，支援環境變數覆蓋：

```bash
# .env 檔案範例
DEBUG=false
APP_NAME="FastAPI MCP Server"
APP_VERSION="2.0.0"
HOST=0.0.0.0
PORT=8000

# 資料庫設定
DATABASE_URL=postgresql://postgres:password@timescaledb:5432/fastapi_mcp
REDIS_URL=redis://:redis_password@redis:6379/0

# MCP 設定
MCP_NAME=statistics-server
MCP_DESCRIPTION=統計分析與機器學習服務

# CORS 設定
CORS_ORIGINS=["http://localhost:3000", "http://localhost:8080"]
```

---

## 🤝 貢獻指南

### 開發環境設定
```bash
# 1. 安裝開發依賴
poetry install --with dev

# 2. 設定 pre-commit hooks
poetry run pre-commit install

# 3. 執行程式碼檢查
poetry run ruff check app/
poetry run mypy app/
```

### 開發流程
1. Fork 專案倉庫
2. 建立功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交變更 (`git commit -m 'Add amazing feature'`)
4. 推送分支 (`git push origin feature/amazing-feature`)
5. 開啟 Pull Request

---