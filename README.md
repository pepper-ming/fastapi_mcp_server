# FastAPI MCP Server

基於 Model Context Protocol (MCP) 的統計分析與機器學習推論服務平台。

## 🌟 專案概述

這是一個基於 FastAPI 和 MCP (Model Context Protocol) 的統計分析與機器學習推論服務平台，提供全面的統計計算、進階分析、時間序列預測和機器學習功能。該平台設計為高效能、可擴展的微服務架構，支援多種統計分析方法和機器學習模型。

## 🚀 主要功能

### 📊 基礎統計分析
- **描述性統計**: 平均值、中位數、標準差、變異數、分位數等
- **假設檢定**: 單樣本 t 檢定、雙樣本 t 檢定、比例檢定等
- **信賴區間**: 多種信賴水準的區間估計

### 🧮 進階統計分析
- **相關性分析**: Pearson、Spearman、Kendall 相關係數
- **迴歸分析**: 
  - 線性迴歸
  - 多項式迴歸
  - Ridge 迴歸
  - Lasso 迴歸
  - 邏輯迴歸
- **殘差分析**: Durbin-Watson 統計量、正態性檢定

### ⏰ 時間序列分析
- **預測模型**: 
  - 線性趨勢預測
  - 移動平均
  - 指數平滑
  - ARIMA 模型
- **異常檢測**: 
  - Z-score 方法
  - IQR 方法
  - 移動平均基線法

### 📈 監控與日誌
- **系統監控**: 即時性能指標追蹤
- **API 監控**: 請求統計、響應時間分析
- **健康檢查**: 全面的服務狀態檢查

## 🛠️ 技術架構

### 核心技術棧
- **Web 框架**: FastAPI 0.115.0
- **MCP 整合**: fastapi-mcp 0.3.0
- **資料處理**: NumPy, Pandas, SciPy
- **機器學習**: scikit-learn
- **資料庫**: TimescaleDB (PostgreSQL)
- **快取**: Redis
- **容器化**: Docker & Docker Compose

### 專案結構
```
fastapi_mcp_server/
├── app/
│   ├── api/                 # API 路由層
│   │   ├── statistics.py    # 基礎統計 API
│   │   ├── advanced_statistics.py  # 進階統計 API
│   │   ├── timeseries.py    # 時間序列 API
│   │   └── monitoring.py    # 監控 API
│   ├── core/                # 核心配置
│   │   ├── settings.py      # 設定管理
│   │   ├── logging.py       # 日誌配置
│   │   └── mcp_config.py    # MCP 配置
│   ├── models/              # 資料模型
│   │   ├── statistics.py    # 統計資料模型
│   │   ├── advanced_statistics.py  # 進階統計模型
│   │   └── timeseries.py    # 時間序列模型
│   ├── services/            # 業務邏輯層
│   │   ├── statistics.py    # 統計服務
│   │   ├── advanced_statistics.py  # 進階統計服務
│   │   └── timeseries.py    # 時間序列服務
│   ├── middleware/          # 中間件
│   └── utils/               # 工具函數
├── tests/                   # 測試套件
│   ├── unit/                # 單元測試
│   └── integration/         # 整合測試
├── scripts/                 # 部署腳本
├── docs/                    # 文件
└── docker-compose.yml       # Docker 配置
```

## 🚀 快速開始

### 環境需求
- Python 3.11+
- Poetry (推薦) 或 pip
- Docker & Docker Compose (用於資料庫服務)

### 安裝與運行

1. **克隆專案**
```bash
git clone <repository-url>
cd fastapi_mcp_server
```

2. **安裝依賴**
```bash
# 使用 Poetry (推薦)
poetry install

# 或使用 pip
pip install -r requirements.txt
```

3. **啟動資料庫服務**
```bash
docker-compose up -d timescaledb redis
```

4. **運行應用程式**
```bash
# 開發模式
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 或直接執行
python -m app.main
```

5. **訪問服務**
- API 文件: http://localhost:8000/docs
- MCP 端點: http://localhost:8000/mcp
- 健康檢查: http://localhost:8000/health

### Docker 部署

```bash
# 完整環境部署
docker-compose up -d

# 僅應用程式
docker-compose up app
```

## 📖 API 使用範例

### 基礎統計分析
```python
import requests

# 描述性統計
response = requests.post(
    "http://localhost:8000/statistics/descriptive",
    json={
        "data": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        "confidence_level": 0.95
    }
)
print(response.json())
```

### 相關性分析
```python
# Pearson 相關性分析
response = requests.post(
    "http://localhost:8000/statistics/advanced/correlation",
    json={
        "x_data": [1, 2, 3, 4, 5],
        "y_data": [2, 4, 6, 8, 10],
        "correlation_type": "pearson",
        "alpha": 0.05
    }
)
print(response.json())
```

### 時間序列預測
```python
# 線性趨勢預測
response = requests.post(
    "http://localhost:8000/timeseries/forecast",
    json={
        "data": [10, 12, 13, 15, 17, 19, 21],
        "timestamps": ["2024-01-01", "2024-01-02", "2024-01-03", 
                      "2024-01-04", "2024-01-05", "2024-01-06", "2024-01-07"],
        "forecast_periods": 3,
        "model_type": "linear_trend"
    }
)
print(response.json())
```

## 🔧 MCP 整合

本專案支援 Model Context Protocol，可作為 MCP 服務器供 AI 助手使用：

### MCP 客戶端配置

```json
{
  "mcpServers": {
    "fastapi-mcp-stats": {
      "command": "python",
      "args": ["-m", "app.main"],
      "env": {
        "MCP_TRANSPORT": "stdio"
      }
    }
  }
}
```

### 可用工具
- `calculate_descriptive_statistics`: 計算描述性統計
- `perform_hypothesis_test`: 執行假設檢定
- `calculate_correlation`: 相關性分析
- `perform_regression`: 迴歸分析
- `forecast_timeseries`: 時間序列預測
- `detect_anomalies`: 異常檢測

## 🧪 測試

```bash
# 運行所有測試
poetry run pytest

# 運行特定測試
poetry run pytest tests/unit/test_statistics_service.py

# 生成覆蓋率報告
poetry run pytest --cov=app --cov-report=html
```

## 📊 監控與健康檢查

### 健康檢查端點
- `GET /health`: 基本健康狀態
- `GET /monitoring/system`: 系統性能指標
- `GET /monitoring/api-stats`: API 使用統計

### 日誌監控
應用程式提供結構化日誌，支援：
- 請求/響應日誌
- 錯誤追蹤
- 性能監控
- MCP 協議日誌

## 🔐 安全性

- CORS 支援可配置
- 輸入資料驗證
- 錯誤處理與資料清理
- 安全的預設配置

## ⚙️ 配置

主要配置項目位於 `app/core/settings.py`：

```python
# 基本設定
APP_NAME: str = "FastAPI MCP Server"
APP_VERSION: str = "0.1.0"
DEBUG: bool = False

# 伺服器設定
HOST: str = "0.0.0.0"
PORT: int = 8000

# 資料庫設定
DATABASE_URL: str = "postgresql+asyncpg://..."

# MCP 設定
MCP_NAME: str = "statistics-server"
MCP_DESCRIPTION: str = "統計分析與機器學習服務"
```

## 尚未開發完畢...
