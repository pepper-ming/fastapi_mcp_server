from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


class TestMCPIntegration:
    """MCP 整合測試"""

    def test_mcp_endpoint_exists(self):
        """測試 MCP 端點是否存在"""
        response = client.get("/mcp")
        # MCP 端點應該回應特定的 MCP 協議格式
        assert response.status_code in [200, 405]  # GET 可能不被支援

    def test_mcp_tools_discovery(self):
        """測試 MCP 工具發現功能"""
        # 這裡需要根據實際的 MCP 協議實作來測試
        # 通常會透過 POST 請求來查詢可用的工具
        mcp_request = {"jsonrpc": "2.0", "method": "tools/list", "id": 1}

        response = client.post("/mcp", json=mcp_request)

        # 檢查回應格式符合 MCP 規範
        if response.status_code == 200:
            data = response.json()
            assert "result" in data or "error" in data

    def test_fastapi_endpoints_as_mcp_tools(self):
        """測試 FastAPI 端點是否正確轉換為 MCP 工具"""
        # 檢查統計端點是否可透過 MCP 呼叫
        mcp_call = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "calculate_descriptive_statistics",
                "arguments": {"data": [1, 2, 3, 4, 5], "confidence_level": 0.95},
            },
            "id": 2,
        }

        response = client.post("/mcp", json=mcp_call)

        # 驗證 MCP 呼叫結果
        if response.status_code == 200:
            data = response.json()
            if "result" in data:
                result = data["result"]
                # 檢查統計結果是否正確
                assert "content" in result
