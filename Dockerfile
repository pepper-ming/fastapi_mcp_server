# 多階段構建：Poetry 依賴管理
FROM python:3.11-slim AS requirements-stage

WORKDIR /tmp

# 安裝 Poetry
RUN pip install poetry

# 複製 Poetry 配置檔案
COPY ./pyproject.toml ./poetry.lock* /tmp/

# 匯出依賴到 requirements.txt
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes

# 生產環境階段
FROM python:3.11-slim AS runtime

# 建立非 root 使用者
RUN addgroup --gid 1001 --system nonroot && \
    adduser --uid 1001 --system --group nonroot

# 設定工作目錄
WORKDIR /code

# 複製 requirements.txt
COPY --from=requirements-stage /tmp/requirements.txt /code/requirements.txt

# 安裝依賴
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# 複製應用程式程式碼
COPY --chown=nonroot:nonroot ./app /code/app

# 建立日誌目錄
RUN mkdir -p /code/logs && chown nonroot:nonroot /code/logs

# 切換到非 root 使用者
USER nonroot:nonroot

# 暴露埠號
EXPOSE 8000

# 健康檢查
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# 執行應用程式
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]