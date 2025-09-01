import logging
import sys
import time
from typing import Dict, Any
from datetime import datetime
from pathlib import Path

class MCPLogger:
    """MCP 專用日誌記錄器"""
    
    def __init__(self, log_level: str = "INFO"):
        self.logger = logging.getLogger("mcp_server")
        self.logger.setLevel(getattr(logging, log_level.upper()))
        
        # 避免重複添加處理器
        if not self.logger.handlers:
            self._setup_handlers()
        
        # MCP 性能度量
        self.metrics = {
            "requests_total": 0,
            "errors_total": 0,
            "avg_response_time": 0.0,
            "last_request_time": None,
            "active_sessions": set(),
        }
    
    def _setup_handlers(self):
        """設定日誌處理器"""
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        
        # 控制台處理器
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # 文件處理器
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        file_handler = logging.FileHandler(
            log_dir / "mcp_server.log", encoding="utf-8"
        )
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
    
    def log_mcp_request(self, session_id: str, action: str, details: Dict[str, Any] = None):
        """記錄 MCP 請求"""
        self.metrics["requests_total"] += 1
        self.metrics["last_request_time"] = datetime.now()
        self.metrics["active_sessions"].add(session_id)
        
        log_data = {
            "session_id": session_id,
            "action": action,
            "timestamp": datetime.now().isoformat(),
        }
        
        if details:
            log_data.update(details)
        
        self.logger.info(f"MCP Request: {log_data}")
    
    def log_mcp_response(self, session_id: str, action: str, response_time: float, success: bool = True):
        """記錄 MCP 回應"""
        # 更新平均回應時間
        if self.metrics["avg_response_time"] == 0:
            self.metrics["avg_response_time"] = response_time
        else:
            total_requests = self.metrics["requests_total"]
            self.metrics["avg_response_time"] = (
                (self.metrics["avg_response_time"] * (total_requests - 1) + response_time)
                / total_requests
            )
        
        if not success:
            self.metrics["errors_total"] += 1
        
        log_data = {
            "session_id": session_id,
            "action": action,
            "response_time": f"{response_time:.3f}s",
            "success": success,
            "timestamp": datetime.now().isoformat(),
        }
        
        level = logging.INFO if success else logging.ERROR
        self.logger.log(level, f"MCP Response: {log_data}")
    
    def log_mcp_error(self, session_id: str, action: str, error: str):
        """記錄 MCP 錯誤"""
        self.metrics["errors_total"] += 1
        
        log_data = {
            "session_id": session_id,
            "action": action,
            "error": error,
            "timestamp": datetime.now().isoformat(),
        }
        
        self.logger.error(f"MCP Error: {log_data}")
    
    def get_metrics(self) -> Dict[str, Any]:
        """取得性能度量"""
        return {
            **self.metrics,
            "active_sessions_count": len(self.metrics["active_sessions"]),
            "active_sessions": list(self.metrics["active_sessions"]),
            "error_rate": (
                self.metrics["errors_total"] / self.metrics["requests_total"]
                if self.metrics["requests_total"] > 0
                else 0
            ),
            "last_request_time": (
                self.metrics["last_request_time"].isoformat()
                if self.metrics["last_request_time"]
                else None
            ),
        }

# 單例模式
mcp_logger = MCPLogger()