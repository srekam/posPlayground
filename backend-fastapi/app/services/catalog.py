"""Catalog Service - Placeholder"""
from typing import Dict, Any
from app.utils.logging import LoggerMixin

class CatalogService(LoggerMixin):
    def __init__(self):
        pass
    
    async def get_packages(self, store_id: str, user) -> list:
        self.logger.info("Getting packages", store_id=store_id)
        return []
    
    async def get_pricing_rules(self, store_id: str, user) -> list:
        self.logger.info("Getting pricing rules", store_id=store_id)
        return []
