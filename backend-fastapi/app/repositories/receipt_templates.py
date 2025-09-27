"""
Receipt Template Repository
"""
from typing import List, Optional

from .base import BaseRepository
from app.models.receipt_templates import ReceiptTemplate, Printer


class ReceiptTemplateRepository(BaseRepository[ReceiptTemplate]):
    """Receipt template repository"""
    
    def __init__(self):
        super().__init__("receipt_templates", ReceiptTemplate)
    
    async def get_by_tenant(self, tenant_id: str) -> List[ReceiptTemplate]:
        """Get templates by tenant"""
        return await self.get_many({"tenant_id": tenant_id, "active": True})
    
    async def get_by_store(self, store_id: str) -> List[ReceiptTemplate]:
        """Get templates by store"""
        return await self.get_many({"store_id": store_id, "active": True})
    
    async def get_by_type(
        self,
        tenant_id: str,
        template_type: str,
        store_id: Optional[str] = None
    ) -> List[ReceiptTemplate]:
        """Get templates by type"""
        query = {"tenant_id": tenant_id, "type": template_type, "active": True}
        if store_id:
            query["$or"] = [
                {"store_id": store_id},
                {"store_id": None}
            ]
        
        return await self.get_many(query)
    
    async def get_default_template(
        self,
        tenant_id: str,
        template_type: str,
        store_id: Optional[str] = None
    ) -> Optional[ReceiptTemplate]:
        """Get default template for type"""
        # Try store-specific template first
        if store_id:
            query = {
                "tenant_id": tenant_id,
                "store_id": store_id,
                "type": template_type,
                "active": True
            }
            store_templates = await self.get_many(query, limit=1)
            if store_templates:
                return store_templates[0]
        
        # Fall back to tenant-level template
        query = {
            "tenant_id": tenant_id,
            "store_id": None,
            "type": template_type,
            "active": True
        }
        return await self.get_many(query, limit=1)[0] if await self.count(query) > 0 else None
    
    async def deactivate(self, template_id: str) -> Optional[ReceiptTemplate]:
        """Deactivate template"""
        return await self.update_by_id(template_id, {"active": False}, "template_id")
    
    async def activate(self, template_id: str) -> Optional[ReceiptTemplate]:
        """Activate template"""
        return await self.update_by_id(template_id, {"active": True}, "template_id")


class PrinterRepository(BaseRepository[Printer]):
    """Printer repository"""
    
    def __init__(self):
        super().__init__("printers", Printer)
    
    async def get_by_store(self, store_id: str) -> List[Printer]:
        """Get printers by store"""
        return await self.get_many({"store_id": store_id, "active": True})
    
    async def get_by_device(self, device_id: str) -> List[Printer]:
        """Get printers by device"""
        return await self.get_many({"device_id": device_id, "active": True})
    
    async def get_by_type(self, store_id: str, printer_type: str) -> List[Printer]:
        """Get printers by type"""
        return await self.get_many({
            "store_id": store_id,
            "type": printer_type,
            "active": True
        })
    
    async def test_connection(self, printer_id: str) -> bool:
        """Test printer connection"""
        # This would implement actual printer connection testing
        # For now, just return True as a placeholder
        return True
    
    async def deactivate(self, printer_id: str) -> Optional[Printer]:
        """Deactivate printer"""
        return await self.update_by_id(printer_id, {"active": False}, "printer_id")
    
    async def activate(self, printer_id: str) -> Optional[Printer]:
        """Activate printer"""
        return await self.update_by_id(printer_id, {"active": True}, "printer_id")
