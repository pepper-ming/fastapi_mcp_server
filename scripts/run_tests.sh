#!/bin/bash

set -e

echo "執行程式碼品質檢查..."

# 執行 Ruff 檢查
echo "執行 Ruff 程式碼檢查..."
poetry run ruff check .

# 執行 Ruff 格式化
echo "執行 Ruff 程式碼格式化..."
poetry run ruff format .

# 執行 MyPy 類型檢查
echo "執行 MyPy 類型檢查..."
poetry run mypy app/

# 執行測試
echo "執行單元測試..."
poetry run pytest tests/ -v --cov=app --cov-report=term-missing

echo "所有檢查完成！"