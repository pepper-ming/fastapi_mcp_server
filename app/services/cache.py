import json
import hashlib
from typing import Optional, Any, Dict
from redis.asyncio import Redis
import pickle
from datetime import timedelta

from app.core.settings import get_settings

settings = get_settings()


class CacheService:
    """Redis 快取服務"""

    def __init__(self):
        self.redis: Optional[Redis] = None

    async def connect(self):
        """連接 Redis"""
        self.redis = Redis.from_url(settings.redis_url, decode_responses=False)

    async def disconnect(self):
        """斷開 Redis 連接"""
        if self.redis:
            await self.redis.close()

    def _generate_key(self, prefix: str, data: Dict[str, Any]) -> str:
        """生成快取鍵值"""
        # 創建資料的哈希值
        data_str = json.dumps(data, sort_keys=True, ensure_ascii=False)
        data_hash = hashlib.md5(data_str.encode()).hexdigest()
        return f"{prefix}:{data_hash}"

    async def get_analysis_result(self, analysis_type: str, input_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """獲取快取的分析結果"""
        if not self.redis:
            return None

        key = self._generate_key(f"analysis:{analysis_type}", input_data)
        cached_data = await self.redis.get(key)

        if cached_data:
            return pickle.loads(cached_data)
        return None

    async def set_analysis_result(
        self,
        analysis_type: str,
        input_data: Dict[str, Any],
        result: Dict[str, Any],
        ttl_seconds: int = 3600  # 1小時過期
    ):
        """快取分析結果"""
        if not self.redis:
            return

        key = self._generate_key(f"analysis:{analysis_type}", input_data)
        serialized_result = pickle.dumps(result)
        await self.redis.setex(key, ttl_seconds, serialized_result)

    async def get_forecast_result(self, series_id: str, model_params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """獲取快取的預測結果"""
        if not self.redis:
            return None

        key = self._generate_key(f"forecast:{series_id}", model_params)
        cached_data = await self.redis.get(key)

        if cached_data:
            return pickle.loads(cached_data)
        return None

    async def set_forecast_result(
        self,
        series_id: str,
        model_params: Dict[str, Any],
        result: Dict[str, Any],
        ttl_seconds: int = 1800  # 30分鐘過期
    ):
        """快取預測結果"""
        if not self.redis:
            return

        key = self._generate_key(f"forecast:{series_id}", model_params)
        serialized_result = pickle.dumps(result)
        await self.redis.setex(key, ttl_seconds, serialized_result)

    async def invalidate_pattern(self, pattern: str):
        """清除符合模式的快取"""
        if not self.redis:
            return

        keys = await self.redis.keys(pattern)
        if keys:
            await self.redis.delete(*keys)

    async def get_cache_stats(self) -> Dict[str, Any]:
        """獲取快取統計資訊"""
        if not self.redis:
            return {}

        info = await self.redis.info('memory')
        return {
            'used_memory': info.get('used_memory', 0),
            'used_memory_human': info.get('used_memory_human', '0B'),
            'total_keys': await self.redis.dbsize()
        }


# 全局快取實例
cache_service = CacheService()