# 轉換至 Alembic 遷移系統指引

## 🎯 目標
將現有的 `Base.metadata.create_all()` 方式轉換為 Alembic 資料庫遷移管理。

## ⚠️ 重要提醒
**此操作需要在自家本機執行，需要資料庫連接！**

## 📋 執行步驟

### 步驟1：確認環境
```bash
# 確認在專案根目錄
cd /path/to/fastapi_mcp_server

# 確認虛擬環境
poetry shell

# 確認資料庫服務運行
docker-compose up -d timescaledb redis
```

### 步驟2：生成初始遷移
```bash
# 自動檢測所有模型並生成遷移
alembic revision --autogenerate -m "Initial migration with all models"
```

**預期輸出**：
```
Generating /path/to/alembic/versions/xxxxx_initial_migration.py ... done
```

### 步驟3：檢查遷移腳本
```bash
# 查看生成的遷移文件
ls alembic/versions/

# 檢查遷移內容（應包含以下表格）：
# - analysis_results
# - timeseries_data  
# - model_training_logs
# - statistics_data
# - performance_metrics
# - mcp_request_logs
```

### 步驟4：執行遷移
```bash
# 執行遷移到最新版本
alembic upgrade head
```

**預期輸出**：
```
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade  -> xxxxx, Initial migration with all models
```

### 步驟5：修改應用程式啟動邏輯

#### 5.1 備份現有 main.py
```bash
cp app/main.py app/main_backup_before_alembic.py
```

#### 5.2 修改 app/main.py
移除以下代碼：
```python
# 移除這段
async with engine.begin() as conn:
    await conn.run_sync(Base.metadata.create_all)
```

替換為註解：
```python
# 資料庫遷移已改用 Alembic 管理
# 執行: alembic upgrade head
```

#### 5.3 更新 lifespan 函數
```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    """應用程式生命週期管理"""
    # 啟動時執行
    print("🚀 FastAPI MCP Server 啟動中...")
    
    # 注意：資料庫 schema 由 Alembic 管理
    # 部署時需要先執行: alembic upgrade head
    
    # 連接快取服務
    await cache_service.connect()
    
    print("✅ 所有服務已啟動")
    
    yield
    
    # 關閉時執行
    print("🛑 FastAPI MCP Server 關閉中...")
    await cache_service.disconnect()
    await engine.dispose()
    print("✅ 所有服務已關閉")
```

### 步驟6：更新 Docker 配置

#### 6.1 修改 docker-compose.yml
```yaml
# FastAPI 應用服務
fastapi-mcp:
  build: .
  container_name: fastapi-mcp-server
  ports:
    - "8000:8000"
  environment:
    - DEBUG=false
    - DATABASE_URL=postgresql://postgres:password@timescaledb:5432/fastapi_mcp
    - REDIS_URL=redis://:redis_password@redis:6379/0
    - HOST=0.0.0.0
    - PORT=8000
  volumes:
    - app_data:/code/data
    - app_logs:/code/logs
    - app_models:/code/models
  depends_on:
    timescaledb:
      condition: service_healthy
    redis:
      condition: service_healthy
  restart: unless-stopped
  networks:
    - mcp_network
  # 添加遷移執行
  command: >
    sh -c "alembic upgrade head && 
           uvicorn app.main:app --host 0.0.0.0 --port 8000"
```

### 步驟7：測試新配置

#### 7.1 停止當前服務
```bash
docker-compose down
```

#### 7.2 重新啟動服務
```bash
docker-compose up -d
```

#### 7.3 檢查日誌
```bash
# 檢查 FastAPI 容器日誌
docker-compose logs fastapi-mcp

# 應該看到：
# INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
# INFO  [alembic.runtime.migration] Will assume transactional DDL.
# 🚀 FastAPI MCP Server 啟動中...
# ✅ 所有服務已啟動
```

#### 7.4 測試 API 端點
```bash
# 測試基礎端點
curl http://localhost:8000/

# 測試健康檢查
curl http://localhost:8000/health

# 測試 MCP 端點
curl http://localhost:8000/mcp
```

## 🔄 日後的工作流程

### 修改資料庫模型後：
```bash
# 1. 生成新的遷移
alembic revision --autogenerate -m "描述你的變更"

# 2. 檢查生成的遷移腳本
cat alembic/versions/latest_migration.py

# 3. 執行遷移
alembic upgrade head

# 4. 重啟應用程式（如果需要）
docker-compose restart fastapi-mcp
```

### 回滾遷移（如果需要）：
```bash
# 回滾到上一個版本
alembic downgrade -1

# 回滾到特定版本
alembic downgrade <revision_id>

# 查看遷移歷史
alembic history
```

## 🛟 故障排除

### 問題1：遷移執行失敗
```bash
# 檢查當前資料庫版本
alembic current

# 查看遷移歷史
alembic history

# 手動標記為已執行（謹慎使用）
alembic stamp head
```

### 問題2：應用程式無法啟動
```bash
# 檢查資料庫連接
docker-compose logs timescaledb

# 檢查應用程式日誌
docker-compose logs fastapi-mcp

# 手動執行遷移
docker-compose exec fastapi-mcp alembic upgrade head
```

## ✅ 完成檢查清單

- [ ] 資料庫服務正常運行
- [ ] 生成初始遷移腳本
- [ ] 執行遷移成功
- [ ] 修改 main.py 移除 create_all
- [ ] 更新 Docker 配置
- [ ] 測試應用程式啟動
- [ ] 測試 API 端點正常
- [ ] 備份重要文件

## 📚 參考資源
- [Alembic 官方文檔](https://alembic.sqlalchemy.org/en/latest/)
- [FastAPI 資料庫指南](https://fastapi.tiangolo.com/tutorial/sql-databases/)
- [Docker Compose 參考](https://docs.docker.com/compose/)

---
**建立日期**: 2025-09-02  
**適用環境**: 自家本機開發環境  
**注意事項**: 需要資料庫連接才能執行