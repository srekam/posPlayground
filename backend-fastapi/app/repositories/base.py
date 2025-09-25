"""
Base Repository Class
"""
from typing import Any, Dict, List, Optional, TypeVar, Generic
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorCollection
from pydantic import BaseModel
from bson import ObjectId
import structlog

from app.db.mongo import get_collection
from app.utils.logging import LoggerMixin

T = TypeVar('T', bound=BaseModel)


class BaseRepository(Generic[T], LoggerMixin):
    """Base repository class with common CRUD operations"""
    
    def __init__(self, collection_name: str, model_class: type[T]):
        self.collection_name = collection_name
        self.model_class = model_class
        self._collection: Optional[AsyncIOMotorCollection] = None
    
    @property
    def collection(self) -> AsyncIOMotorCollection:
        """Get MongoDB collection"""
        if self._collection is None:
            self._collection = get_collection(self.collection_name)
        return self._collection
    
    async def create(self, document: T) -> T:
        """Create a new document"""
        try:
            document_dict = document.dict(by_alias=True, exclude={"id"})
            result = await self.collection.insert_one(document_dict)
            
            # Fetch the created document
            created_doc = await self.collection.find_one({"_id": result.inserted_id})
            return self.model_class(**created_doc)
            
        except Exception as e:
            self.logger.error("Error creating document", error=str(e), collection=self.collection_name)
            raise
    
    async def get_by_id(self, document_id: str, id_field: str = "_id") -> Optional[T]:
        """Get document by ID"""
        try:
            # Handle ObjectId conversion
            if id_field == "_id":
                try:
                    document_id = ObjectId(document_id)
                except:
                    pass
            
            query = {id_field: document_id}
            document = await self.collection.find_one(query)
            
            if document:
                return self.model_class(**document)
            return None
            
        except Exception as e:
            self.logger.error("Error getting document by ID", error=str(e), document_id=document_id)
            raise
    
    async def get_by_field(self, field: str, value: Any) -> Optional[T]:
        """Get document by field value"""
        try:
            query = {field: value}
            document = await self.collection.find_one(query)
            
            if document:
                return self.model_class(**document)
            return None
            
        except Exception as e:
            self.logger.error("Error getting document by field", error=str(e), field=field, value=value)
            raise
    
    async def get_many(
        self,
        query: Optional[Dict[str, Any]] = None,
        skip: int = 0,
        limit: int = 100,
        sort: Optional[List[tuple]] = None
    ) -> List[T]:
        """Get multiple documents"""
        try:
            if query is None:
                query = {}
            
            cursor = self.collection.find(query)
            
            if sort:
                cursor = cursor.sort(sort)
            
            cursor = cursor.skip(skip).limit(limit)
            documents = await cursor.to_list(length=limit)
            
            return [self.model_class(**doc) for doc in documents]
            
        except Exception as e:
            self.logger.error("Error getting multiple documents", error=str(e), query=query)
            raise
    
    async def update_by_id(
        self,
        document_id: str,
        update_data: Dict[str, Any],
        id_field: str = "_id"
    ) -> Optional[T]:
        """Update document by ID"""
        try:
            # Handle ObjectId conversion
            if id_field == "_id":
                try:
                    document_id = ObjectId(document_id)
                except:
                    pass
            
            # Add updated_at timestamp
            update_data["updated_at"] = datetime.utcnow()
            
            query = {id_field: document_id}
            result = await self.collection.update_one(query, {"$set": update_data})
            
            if result.modified_count > 0:
                # Return updated document
                updated_doc = await self.collection.find_one(query)
                return self.model_class(**updated_doc)
            return None
            
        except Exception as e:
            self.logger.error("Error updating document", error=str(e), document_id=document_id)
            raise
    
    async def delete_by_id(self, document_id: str, id_field: str = "_id") -> bool:
        """Delete document by ID"""
        try:
            # Handle ObjectId conversion
            if id_field == "_id":
                try:
                    document_id = ObjectId(document_id)
                except:
                    pass
            
            query = {id_field: document_id}
            result = await self.collection.delete_one(query)
            
            return result.deleted_count > 0
            
        except Exception as e:
            self.logger.error("Error deleting document", error=str(e), document_id=document_id)
            raise
    
    async def count(self, query: Optional[Dict[str, Any]] = None) -> int:
        """Count documents"""
        try:
            if query is None:
                query = {}
            
            return await self.collection.count_documents(query)
            
        except Exception as e:
            self.logger.error("Error counting documents", error=str(e), query=query)
            raise
    
    async def exists(self, query: Dict[str, Any]) -> bool:
        """Check if document exists"""
        try:
            count = await self.collection.count_documents(query, limit=1)
            return count > 0
            
        except Exception as e:
            self.logger.error("Error checking document existence", error=str(e), query=query)
            raise
    
    async def aggregate(self, pipeline: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Run aggregation pipeline"""
        try:
            cursor = self.collection.aggregate(pipeline)
            return await cursor.to_list(length=None)
            
        except Exception as e:
            self.logger.error("Error running aggregation", error=str(e), pipeline=pipeline)
            raise
    
    async def create_index(self, keys: List[tuple], **kwargs) -> str:
        """Create database index"""
        try:
            return await self.collection.create_index(keys, **kwargs)
            
        except Exception as e:
            self.logger.error("Error creating index", error=str(e), keys=keys)
            raise
    
    async def find_one_and_update(
        self,
        query: Dict[str, Any],
        update: Dict[str, Any],
        return_document: bool = True
    ) -> Optional[T]:
        """Find one document and update it"""
        try:
            from pymongo import ReturnDocument
            
            return_doc = ReturnDocument.AFTER if return_document else ReturnDocument.BEFORE
            
            # Add updated_at timestamp
            if "$set" in update:
                update["$set"]["updated_at"] = datetime.utcnow()
            else:
                update["$set"] = {"updated_at": datetime.utcnow()}
            
            document = await self.collection.find_one_and_update(
                query,
                update,
                return_document=return_doc
            )
            
            if document:
                return self.model_class(**document)
            return None
            
        except Exception as e:
            self.logger.error("Error finding and updating document", error=str(e), query=query)
            raise
