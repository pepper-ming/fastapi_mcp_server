import asyncio
from functools import wraps
from typing import Callable, Any, Dict, Optional
import inspect

from app.services.cache import cache_service


def cache_analysis_result(
    analysis_type: str,
    ttl_seconds: int = 3600,
    cache_key_fields: Optional[list] = None
):
    """分析結果快取裝飾器"""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 提取快取鍵值所需的欄位
            if cache_key_fields:
                cache_data = {}
                # 從函數參數中提取指定欄位
                sig = inspect.signature(func)
                bound_args = sig.bind(*args, **kwargs)
                bound_args.apply_defaults()

                for field in cache_key_fields:
                    if hasattr(bound_args.arguments.get('request', {}), field):
                        cache_data[field] = getattr(bound_args.arguments['request'], field)
                    elif field in bound_args.arguments:
                        cache_data[field] = bound_args.arguments[field]
            else:
                # 使用所有參數作為快取鍵
                cache_data = dict(kwargs)
                if args:
                    cache_data['args'] = args

            # 嘗試從快取獲取結果
            cached_result = await cache_service.get_analysis_result(analysis_type, cache_data)
            if cached_result:
                return cached_result

            # 執行實際函數
            result = await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)

            # 快取結果
            if hasattr(result, 'dict'):
                result_dict = result.dict()
            elif isinstance(result, dict):
                result_dict = result
            else:
                result_dict = result

            await cache_service.set_analysis_result(analysis_type, cache_data, result_dict, ttl_seconds)

            return result

        return wrapper
    return decorator


def cache_forecast_result(ttl_seconds: int = 1800):
    """預測結果快取裝飾器"""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 提取序列ID和模型參數
            request = kwargs.get('request') or (args[0] if args else None)
            if not request:
                return await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)

            series_id = request.timeseries.series_id
            model_params = {
                'model_type': request.model_type,
                'forecast_periods': request.forecast_periods,
                'confidence_level': request.confidence_level
            }

            # 從快取獲取結果
            cached_result = await cache_service.get_forecast_result(series_id, model_params)
            if cached_result:
                return cached_result

            # 執行預測
            result = await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)

            # 快取結果
            result_dict = result.dict() if hasattr(result, 'dict') else result
            await cache_service.set_forecast_result(series_id, model_params, result_dict, ttl_seconds)

            return result

        return wrapper
    return decorator