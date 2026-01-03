import os
import json
import hashlib
import redis.asyncio as redis
from loguru import logger
from typing import Optional, Any

class CacheManager:
    def __init__(self):
        self.redis_url = os.getenv("REDIS_URL")
        self.client: Optional[redis.Redis] = None
        self._enabled = False
        
        if self.redis_url:
            try:
                self.client = redis.from_url(self.redis_url, decode_responses=False)
                self._enabled = True
                logger.info("🚀 Redis Cache Manager inicializado com sucesso.")
            except Exception as e:
                logger.error(f"❌ Falha ao conectar ao Redis: {e}")
        else:
            logger.warning("⚠️ REDIS_URL não configurada. Cache desabilitado.")

    def _hash_key(self, prefix: str, data: str) -> str:
        return f"treq:{prefix}:{hashlib.sha256(data.encode()).hexdigest()[:16]}"

    async def get(self, prefix: str, key_data: str) -> Optional[Any]:
        if not self._enabled or not self.client:
            return None
        
        key = self._hash_key(prefix, key_data)
        try:
            cached = await self.client.get(key)
            if cached:
                logger.debug(f"🎯 Cache Hit: {key}")
                return json.loads(cached)
        except Exception as e:
            logger.error(f"Erro ao ler cache: {e}")
        return None

    async def set(self, prefix: str, key_data: str, value: Any, ttl: int = 3600):
        if not self._enabled or not self.client:
            return
        
        key = self._hash_key(prefix, key_data)
        try:
            await self.client.setex(key, ttl, json.dumps(value))
            logger.debug(f"💾 Cache Set: {key} (TTL: {ttl}s)")
        except Exception as e:
            logger.error(f"Erro ao gravar cache: {e}")

# Instância Global
cache_manager = CacheManager()
