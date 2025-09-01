from typing import List, Optional
from pydantic import BaseModel


class MCPToolConfig(BaseModel):
    """MCP 工具暴露配置"""
    
    # 包含的操作 ID
    include_operations: Optional[List[str]] = [
        "calculate_descriptive_statistics",
        "perform_hypothesis_test",
        "get_supported_tests"
    ]
    
    # 包含的標籤
    include_tags: Optional[List[str]] = ["統計分析"]
    
    # 排除的標籤
    exclude_tags: Optional[List[str]] = ["內部", "測試"]
    
    # 是否包含完整回應架構描述
    describe_all_responses: bool = True
    
    # 是否包含完整 JSON 架構
    describe_full_response_schema: bool = False