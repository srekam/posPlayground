"""
Provider Repository (Reports & Analytics)
"""
from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
import structlog

from app.repositories.base import BaseRepository
from app.models.provider import ReportTemplate, ReportInstance, DashboardWidget, ExportFile
from app.utils.logging import LoggerMixin

logger = structlog.get_logger(__name__)


class ProviderRepository(BaseRepository, LoggerMixin):
    """Provider repository for reports and analytics"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "report_templates")
        self.instances_collection = db["report_instances"]
        self.widgets_collection = db["dashboard_widgets"]
        self.exports_collection = db["export_files"]
    
    # Report Template methods
    async def get_template_by_id(self, template_id: str) -> Optional[ReportTemplate]:
        """Get report template by ID"""
        return await self.get_by_id(template_id)
    
    async def get_templates_by_category(self, category: str, skip: int = 0, limit: int = 100) -> List[ReportTemplate]:
        """Get templates by category"""
        cursor = self.collection.find({"category": category}).skip(skip).limit(limit)
        return [ReportTemplate(**doc) async for doc in cursor]
    
    async def get_templates_by_creator(self, created_by: str, skip: int = 0, limit: int = 100) -> List[ReportTemplate]:
        """Get templates by creator"""
        cursor = self.collection.find({"created_by": created_by}).skip(skip).limit(limit)
        return [ReportTemplate(**doc) async for doc in cursor]
    
    async def create_template(self, template: ReportTemplate) -> ReportTemplate:
        """Create a new report template"""
        return await self.create(template)
    
    async def update_template(self, template_id: str, updates: Dict[str, Any]) -> Optional[ReportTemplate]:
        """Update report template"""
        return await self.update_by_id(template_id, updates)
    
    async def delete_template(self, template_id: str) -> bool:
        """Delete report template"""
        return await self.delete_by_id(template_id)
    
    # Report Instance methods
    async def get_instance_by_id(self, instance_id: str) -> Optional[ReportInstance]:
        """Get report instance by ID"""
        doc = await self.instances_collection.find_one({"_id": instance_id})
        return ReportInstance(**doc) if doc else None
    
    async def get_instances_by_template(self, template_id: str, skip: int = 0, limit: int = 100) -> List[ReportInstance]:
        """Get instances by template"""
        cursor = self.instances_collection.find({"template_id": template_id}).skip(skip).limit(limit)
        return [ReportInstance(**doc) async for doc in cursor]
    
    async def get_instances_by_user(self, generated_by: str, skip: int = 0, limit: int = 100) -> List[ReportInstance]:
        """Get instances by user"""
        cursor = self.instances_collection.find({"generated_by": generated_by}).skip(skip).limit(limit)
        return [ReportInstance(**doc) async for doc in cursor]
    
    async def create_instance(self, instance: ReportInstance) -> ReportInstance:
        """Create a new report instance"""
        doc = await self.instances_collection.insert_one(instance.dict())
        instance.id = doc.inserted_id
        return instance
    
    async def update_instance(self, instance_id: str, updates: Dict[str, Any]) -> Optional[ReportInstance]:
        """Update report instance"""
        result = await self.instances_collection.update_one(
            {"_id": instance_id},
            {"$set": updates}
        )
        if result.modified_count:
            doc = await self.instances_collection.find_one({"_id": instance_id})
            return ReportInstance(**doc) if doc else None
        return None
    
    # Dashboard Widget methods
    async def get_widget_by_id(self, widget_id: str) -> Optional[DashboardWidget]:
        """Get dashboard widget by ID"""
        doc = await self.widgets_collection.find_one({"_id": widget_id})
        return DashboardWidget(**doc) if doc else None
    
    async def get_widgets_by_category(self, category: str, skip: int = 0, limit: int = 100) -> List[DashboardWidget]:
        """Get widgets by category"""
        cursor = self.widgets_collection.find({"category": category}).skip(skip).limit(limit)
        return [DashboardWidget(**doc) async for doc in cursor]
    
    async def get_widgets_by_creator(self, created_by: str, skip: int = 0, limit: int = 100) -> List[DashboardWidget]:
        """Get widgets by creator"""
        cursor = self.widgets_collection.find({"created_by": created_by}).skip(skip).limit(limit)
        return [DashboardWidget(**doc) async for doc in cursor]
    
    async def create_widget(self, widget: DashboardWidget) -> DashboardWidget:
        """Create a new dashboard widget"""
        doc = await self.widgets_collection.insert_one(widget.dict())
        widget.id = doc.inserted_id
        return widget
    
    async def update_widget(self, widget_id: str, updates: Dict[str, Any]) -> Optional[DashboardWidget]:
        """Update dashboard widget"""
        result = await self.widgets_collection.update_one(
            {"_id": widget_id},
            {"$set": updates}
        )
        if result.modified_count:
            doc = await self.widgets_collection.find_one({"_id": widget_id})
            return DashboardWidget(**doc) if doc else None
        return None
    
    # Export File methods
    async def get_export_by_id(self, file_id: str) -> Optional[ExportFile]:
        """Get export file by ID"""
        doc = await self.exports_collection.find_one({"_id": file_id})
        return ExportFile(**doc) if doc else None
    
    async def get_exports_by_instance(self, instance_id: str) -> List[ExportFile]:
        """Get exports by instance"""
        cursor = self.exports_collection.find({"instance_id": instance_id})
        return [ExportFile(**doc) async for doc in cursor]
    
    async def create_export(self, export: ExportFile) -> ExportFile:
        """Create a new export file"""
        doc = await self.exports_collection.insert_one(export.dict())
        export.id = doc.inserted_id
        return export
    
    # Analytics methods
    async def get_template_stats(self) -> Dict[str, Any]:
        """Get template statistics"""
        pipeline = [
            {
                "$group": {
                    "_id": None,
                    "total_templates": {"$sum": 1},
                    "active_templates": {
                        "$sum": {"$cond": [{"$eq": ["$is_active", True]}, 1, 0]}
                    }
                }
            }
        ]
        
        result = await self.collection.aggregate(pipeline).to_list(1)
        return result[0] if result else {
            "total_templates": 0,
            "active_templates": 0
        }
    
    async def get_widget_stats(self) -> Dict[str, Any]:
        """Get widget statistics"""
        pipeline = [
            {
                "$group": {
                    "_id": None,
                    "total_widgets": {"$sum": 1},
                    "active_widgets": {
                        "$sum": {"$cond": [{"$eq": ["$is_active", True]}, 1, 0]}
                    },
                    "total_usage": {"$sum": "$usage_count"}
                }
            }
        ]
        
        result = await self.widgets_collection.aggregate(pipeline).to_list(1)
        return result[0] if result else {
            "total_widgets": 0,
            "active_widgets": 0,
            "total_usage": 0
        }
