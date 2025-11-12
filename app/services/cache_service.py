"""
缓存服务 - 简单的内存缓存
"""

from typing import Any, Optional
from datetime import datetime, timedelta
import threading


class CacheItem:
    """缓存项"""
    
    def __init__(self, value: Any, ttl: int = 300):
        """
        初始化缓存项
        
        Args:
            value: 缓存值
            ttl: 过期时间（秒），默认5分钟
        """
        self.value = value
        self.created_at = datetime.now()
        self.ttl = timedelta(seconds=ttl)
    
    def is_expired(self) -> bool:
        """检查是否过期"""
        return datetime.now() - self.created_at > self.ttl


class CacheService:
    """简单的内存缓存服务"""
    
    def __init__(self):
        self._cache: dict[str, CacheItem] = {}
        self._lock = threading.Lock()
    
    def get(self, key: str) -> Optional[Any]:
        """
        获取缓存值
        
        Args:
            key: 缓存键
            
        Returns:
            缓存值，如果不存在或已过期返回None
        """
        with self._lock:
            item = self._cache.get(key)
            if item is None:
                return None
            
            if item.is_expired():
                del self._cache[key]
                return None
            
            return item.value
    
    def set(self, key: str, value: Any, ttl: int = 300):
        """
        设置缓存值
        
        Args:
            key: 缓存键
            value: 缓存值
            ttl: 过期时间（秒），默认5分钟
        """
        with self._lock:
            self._cache[key] = CacheItem(value, ttl)
    
    def delete(self, key: str):
        """
        删除缓存值
        
        Args:
            key: 缓存键
        """
        with self._lock:
            if key in self._cache:
                del self._cache[key]
    
    def clear(self):
        """清空所有缓存"""
        with self._lock:
            self._cache.clear()
    
    def cleanup_expired(self):
        """清理过期的缓存项"""
        with self._lock:
            expired_keys = [
                key for key, item in self._cache.items()
                if item.is_expired()
            ]
            for key in expired_keys:
                del self._cache[key]


# 全局缓存实例
_cache_service: Optional[CacheService] = None


def get_cache_service() -> CacheService:
    """获取缓存服务实例（单例模式）"""
    global _cache_service
    if _cache_service is None:
        _cache_service = CacheService()
    return _cache_service

