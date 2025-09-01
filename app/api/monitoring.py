from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from datetime import datetime

from app.core.logging import mcp_logger

router = APIRouter(prefix="/monitoring", tags=["監控"])

@router.get("/mcp/metrics", operation_id="get_mcp_metrics")
async def get_mcp_metrics() -> Dict[str, Any]:
    """取得 MCP 性能度量
    
    Returns:
        Dict containing MCP performance metrics:
        - requests_total: 總請求數
        - errors_total: 總錯誤數  
        - error_rate: 錯誤率
        - avg_response_time: 平均回應時間
        - active_sessions_count: 活躍 session 數量
        - last_request_time: 最後請求時間
    """
    try:
        metrics = mcp_logger.get_metrics()
        return {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "metrics": metrics
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get metrics: {str(e)}")

@router.get("/mcp/status", operation_id="get_mcp_status")  
async def get_mcp_status() -> Dict[str, Any]:
    """取得 MCP 服務狀態"""
    try:
        metrics = mcp_logger.get_metrics()
        
        # 判斷服務健康狀態
        health_status = "healthy"
        if metrics["error_rate"] > 0.1:  # 錯誤率超過 10%
            health_status = "degraded"
        elif metrics["error_rate"] > 0.2:  # 錯誤率超過 20%
            health_status = "unhealthy"
        
        return {
            "status": health_status,
            "timestamp": datetime.now().isoformat(),
            "uptime_info": {
                "total_requests": metrics["requests_total"],
                "active_sessions": metrics["active_sessions_count"],
                "error_rate_percentage": round(metrics["error_rate"] * 100, 2),
                "avg_response_time_ms": round(metrics["avg_response_time"] * 1000, 2),
            },
            "last_activity": metrics["last_request_time"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get status: {str(e)}")

@router.post("/mcp/reset-metrics", operation_id="reset_mcp_metrics")
async def reset_mcp_metrics() -> Dict[str, str]:
    """重置 MCP 性能度量"""
    try:
        # 重置度量
        mcp_logger.metrics = {
            "requests_total": 0,
            "errors_total": 0,
            "avg_response_time": 0.0,
            "last_request_time": None,
            "active_sessions": set(),
        }
        
        mcp_logger.logger.info("MCP metrics have been reset")
        
        return {
            "status": "success", 
            "message": "MCP metrics have been reset",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to reset metrics: {str(e)}")

@router.get("/health", operation_id="monitoring_health_check")
async def monitoring_health_check() -> Dict[str, str]:
    """監控系統健康檢查"""
    return {
        "status": "healthy",
        "service": "MCP Monitoring",
        "timestamp": datetime.now().isoformat()
    }