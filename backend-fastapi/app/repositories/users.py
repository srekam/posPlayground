"""
User Repository
"""
from typing import Optional, List
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.models.core import Employee, Role, Tenant, Store, Device
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository):
    """User repository"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__("employees", Employee)
        self.db = db
        self.roles_repo = BaseRepository("roles", Role)
        self.tenants_repo = BaseRepository("tenants", Tenant)
        self.stores_repo = BaseRepository("stores", Store)
        self.devices_repo = BaseRepository("devices", Device)
    
    async def get_by_email(self, email: str) -> Optional[Employee]:
        """Get employee by email"""
        return await self.get_by_field("email", email)
    
    async def get_by_employee_id(self, employee_id: str) -> Optional[Employee]:
        """Get employee by employee ID"""
        return await self.get_by_field("employee_id", employee_id)
    
    async def get_employees_by_store(
        self,
        tenant_id: str,
        store_id: str,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Employee]:
        """Get employees by store"""
        query = {"tenant_id": tenant_id, "store_id": store_id}
        if status:
            query["status"] = status
        
        return await self.get_many(query, skip=skip, limit=limit)
    
    async def get_employees_by_role(
        self,
        tenant_id: str,
        role: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Employee]:
        """Get employees by role"""
        query = {"tenant_id": tenant_id, "roles": role}
        return await self.get_many(query, skip=skip, limit=limit)
    
    async def update_employee_status(self, employee_id: str, status: str) -> Optional[Employee]:
        """Update employee status"""
        return await self.update_by_id(
            employee_id,
            {"status": status},
            "employee_id"
        )
    
    async def update_employee_roles(
        self,
        employee_id: str,
        roles: List[str]
    ) -> Optional[Employee]:
        """Update employee roles"""
        return await self.update_by_id(
            employee_id,
            {"roles": roles},
            "employee_id"
        )
    
    async def update_employee_permissions(
        self,
        employee_id: str,
        permissions: List[str]
    ) -> Optional[Employee]:
        """Update employee permissions"""
        return await self.update_by_id(
            employee_id,
            {"permissions": permissions},
            "employee_id"
        )
    
    # Role operations
    async def get_role_by_id(self, role_id: str) -> Optional[Role]:
        """Get role by ID"""
        return await self.roles_repo.get_by_field("role_id", role_id)
    
    async def get_roles_by_tenant(
        self,
        tenant_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Role]:
        """Get roles by tenant"""
        query = {"tenant_id": tenant_id}
        return await self.roles_repo.get_many(query, skip=skip, limit=limit)
    
    async def create_role(self, role: Role) -> Role:
        """Create a new role"""
        return await self.roles_repo.create(role)
    
    async def update_role(
        self,
        role_id: str,
        update_data: dict
    ) -> Optional[Role]:
        """Update role"""
        return await self.roles_repo.update_by_id(
            role_id,
            update_data,
            "role_id"
        )
    
    async def delete_role(self, role_id: str) -> bool:
        """Delete role"""
        return await self.roles_repo.delete_by_id(role_id, "role_id")
    
    # Tenant operations
    async def get_tenant_by_id(self, tenant_id: str) -> Optional[Tenant]:
        """Get tenant by ID"""
        return await self.tenants_repo.get_by_field("tenant_id", tenant_id)
    
    async def get_tenants(self, skip: int = 0, limit: int = 100) -> List[Tenant]:
        """Get all tenants"""
        return await self.tenants_repo.get_many(skip=skip, limit=limit)
    
    async def create_tenant(self, tenant: Tenant) -> Tenant:
        """Create a new tenant"""
        return await self.tenants_repo.create(tenant)
    
    async def update_tenant_status(self, tenant_id: str, status: str) -> Optional[Tenant]:
        """Update tenant status"""
        return await self.tenants_repo.update_by_id(
            tenant_id,
            {"status": status},
            "tenant_id"
        )
    
    # Store operations
    async def get_store_by_id(self, store_id: str) -> Optional[Store]:
        """Get store by ID"""
        return await self.stores_repo.get_by_field("store_id", store_id)
    
    async def get_stores_by_tenant(
        self,
        tenant_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Store]:
        """Get stores by tenant"""
        query = {"tenant_id": tenant_id}
        return await self.stores_repo.get_many(query, skip=skip, limit=limit)
    
    async def create_store(self, store: Store) -> Store:
        """Create a new store"""
        return await self.stores_repo.create(store)
    
    async def update_store_status(self, store_id: str, status: str) -> Optional[Store]:
        """Update store status"""
        return await self.stores_repo.update_by_id(
            store_id,
            {"status": status},
            "store_id"
        )
    
    # Device operations
    async def get_device_by_id(self, device_id: str) -> Optional[Device]:
        """Get device by ID"""
        return await self.devices_repo.get_by_field("device_id", device_id)
    
    async def get_devices_by_store(
        self,
        tenant_id: str,
        store_id: str,
        device_type: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Device]:
        """Get devices by store"""
        query = {"tenant_id": tenant_id, "store_id": store_id}
        if device_type:
            query["type"] = device_type
        
        return await self.devices_repo.get_many(query, skip=skip, limit=limit)
    
    async def create_device(self, device: Device) -> Device:
        """Create a new device"""
        return await self.devices_repo.create(device)
    
    async def update_device_last_seen(self, device_id: str) -> Optional[Device]:
        """Update device last seen timestamp"""
        from datetime import datetime
        return await self.devices_repo.update_by_id(
            device_id,
            {"last_seen": datetime.utcnow()},
            "device_id"
        )
    
    async def update_device_status(self, device_id: str, status: str) -> Optional[Device]:
        """Update device status"""
        return await self.devices_repo.update_by_id(
            device_id,
            {"status": status},
            "device_id"
        )
