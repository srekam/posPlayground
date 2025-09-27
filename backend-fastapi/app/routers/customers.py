"""
Customer Router
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from ulid import ULID

from app.models.customers import (
    Customer, CustomerCreateRequest, CustomerUpdateRequest,
    CustomerResponse, CustomerSearchRequest
)
from app.repositories.customers import CustomerRepository
from app.utils.errors import PlayParkException, ErrorCode
from app.deps import get_current_user, get_db

router = APIRouter()


@router.post("/", response_model=CustomerResponse, status_code=201)
async def create_customer(
    customer_data: CustomerCreateRequest,
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Create a new customer"""
    try:
        customer_repo = CustomerRepository()
        
        # Check if customer with same email already exists
        if customer_data.email:
            existing_customer = await customer_repo.get_by_email(
                current_user.tenant_id, customer_data.email
            )
            if existing_customer:
                raise PlayParkException(
                    error_code=ErrorCode.E_DUPLICATE,
                    message="Customer with this email already exists",
                    status_code=400
                )
        
        # Check if customer with same phone already exists
        if customer_data.phone:
            existing_customer = await customer_repo.get_by_phone(
                current_user.tenant_id, customer_data.phone
            )
            if existing_customer:
                raise PlayParkException(
                    error_code=ErrorCode.E_DUPLICATE,
                    message="Customer with this phone already exists",
                    status_code=400
                )
        
        # Generate customer ID
        customer_id = str(ULID())
        
        # Create customer document
        customer = Customer(
            customer_id=customer_id,
            tenant_id=current_user.tenant_id,
            name=customer_data.name,
            email=customer_data.email,
            phone=customer_data.phone,
            address=customer_data.address,
            date_of_birth=customer_data.date_of_birth,
            gender=customer_data.gender,
            preferences=customer_data.preferences,
            notes=customer_data.notes
        )
        
        created_customer = await customer_repo.create(customer)
        
        return CustomerResponse(
            customer_id=created_customer.customer_id,
            name=created_customer.name,
            email=created_customer.email,
            phone=created_customer.phone,
            address=created_customer.address,
            date_of_birth=created_customer.date_of_birth,
            gender=created_customer.gender,
            preferences=created_customer.preferences,
            loyalty_points=created_customer.loyalty_points,
            total_spent=created_customer.total_spent,
            visit_count=created_customer.visit_count,
            last_visit=created_customer.last_visit,
            notes=created_customer.notes,
            active=created_customer.active,
            created_at=created_customer.created_at,
            updated_at=created_customer.updated_at
        )
        
    except PlayParkException:
        raise
    except Exception as e:
        raise PlayParkException(
            error_code=ErrorCode.INTERNAL_ERROR,
            message="Failed to create customer",
            details={"error": str(e)}
        )


@router.get("/", response_model=List[CustomerResponse])
async def get_customers(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    active_only: bool = Query(True),
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get customers"""
    try:
        customer_repo = CustomerRepository()
        
        if active_only:
            customers = await customer_repo.get_active_customers(
                current_user.tenant_id, skip, limit
            )
        else:
            customers = await customer_repo.get_many(
                {"tenant_id": current_user.tenant_id}, skip, limit
            )
        
        return [
            CustomerResponse(
                customer_id=c.customer_id,
                name=c.name,
                email=c.email,
                phone=c.phone,
                address=c.address,
                date_of_birth=c.date_of_birth,
                gender=c.gender,
                preferences=c.preferences,
                loyalty_points=c.loyalty_points,
                total_spent=c.total_spent,
                visit_count=c.visit_count,
                last_visit=c.last_visit,
                notes=c.notes,
                active=c.active,
                created_at=c.created_at,
                updated_at=c.updated_at
            )
            for c in customers
        ]
        
    except Exception as e:
        raise PlayParkException(
            error_code=ErrorCode.INTERNAL_ERROR,
            message="Failed to retrieve customers",
            details={"error": str(e)}
        )


@router.get("/search", response_model=List[CustomerResponse])
async def search_customers(
    query: str = Query(..., min_length=1),
    limit: int = Query(20, ge=1, le=100),
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Search customers by name, phone, or email"""
    try:
        customer_repo = CustomerRepository()
        
        customers = await customer_repo.search_customers(
            current_user.tenant_id, query, 0, limit
        )
        
        return [
            CustomerResponse(
                customer_id=c.customer_id,
                name=c.name,
                email=c.email,
                phone=c.phone,
                address=c.address,
                date_of_birth=c.date_of_birth,
                gender=c.gender,
                preferences=c.preferences,
                loyalty_points=c.loyalty_points,
                total_spent=c.total_spent,
                visit_count=c.visit_count,
                last_visit=c.last_visit,
                notes=c.notes,
                active=c.active,
                created_at=c.created_at,
                updated_at=c.updated_at
            )
            for c in customers
        ]
        
    except Exception as e:
        raise PlayParkException(
            error_code=ErrorCode.INTERNAL_ERROR,
            message="Failed to search customers",
            details={"error": str(e)}
        )


@router.get("/{customer_id}", response_model=CustomerResponse)
async def get_customer(
    customer_id: str,
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get customer by ID"""
    try:
        customer_repo = CustomerRepository()
        customer = await customer_repo.get_by_field("customer_id", customer_id)
        
        if not customer:
            raise PlayParkException(
                error_code=ErrorCode.NOT_FOUND,
                message="Customer not found",
                status_code=404
            )
        
        # Check tenant access
        if customer.tenant_id != current_user.tenant_id:
            raise PlayParkException(
                error_code=ErrorCode.E_PERMISSION,
                message="Access denied",
                status_code=403
            )
        
        return CustomerResponse(
            customer_id=customer.customer_id,
            name=customer.name,
            email=customer.email,
            phone=customer.phone,
            address=customer.address,
            date_of_birth=customer.date_of_birth,
            gender=customer.gender,
            preferences=customer.preferences,
            loyalty_points=customer.loyalty_points,
            total_spent=customer.total_spent,
            visit_count=customer.visit_count,
            last_visit=customer.last_visit,
            notes=customer.notes,
            active=customer.active,
            created_at=customer.created_at,
            updated_at=customer.updated_at
        )
        
    except PlayParkException:
        raise
    except Exception as e:
        raise PlayParkException(
            error_code=ErrorCode.INTERNAL_ERROR,
            message="Failed to retrieve customer",
            details={"error": str(e)}
        )


@router.put("/{customer_id}", response_model=CustomerResponse)
async def update_customer(
    customer_id: str,
    customer_data: CustomerUpdateRequest,
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Update customer"""
    try:
        customer_repo = CustomerRepository()
        
        # Get existing customer
        existing_customer = await customer_repo.get_by_field("customer_id", customer_id)
        if not existing_customer:
            raise PlayParkException(
                error_code=ErrorCode.NOT_FOUND,
                message="Customer not found",
                status_code=404
            )
        
        # Check tenant access
        if existing_customer.tenant_id != current_user.tenant_id:
            raise PlayParkException(
                error_code=ErrorCode.E_PERMISSION,
                message="Access denied",
                status_code=403
            )
        
        # Check for duplicate email
        if customer_data.email and customer_data.email != existing_customer.email:
            duplicate_customer = await customer_repo.get_by_email(
                current_user.tenant_id, customer_data.email
            )
            if duplicate_customer:
                raise PlayParkException(
                    error_code=ErrorCode.E_DUPLICATE,
                    message="Customer with this email already exists",
                    status_code=400
                )
        
        # Check for duplicate phone
        if customer_data.phone and customer_data.phone != existing_customer.phone:
            duplicate_customer = await customer_repo.get_by_phone(
                current_user.tenant_id, customer_data.phone
            )
            if duplicate_customer:
                raise PlayParkException(
                    error_code=ErrorCode.E_DUPLICATE,
                    message="Customer with this phone already exists",
                    status_code=400
                )
        
        # Prepare update data
        update_data = {}
        if customer_data.name is not None:
            update_data["name"] = customer_data.name
        if customer_data.email is not None:
            update_data["email"] = customer_data.email
        if customer_data.phone is not None:
            update_data["phone"] = customer_data.phone
        if customer_data.address is not None:
            update_data["address"] = customer_data.address
        if customer_data.date_of_birth is not None:
            update_data["date_of_birth"] = customer_data.date_of_birth
        if customer_data.gender is not None:
            update_data["gender"] = customer_data.gender
        if customer_data.preferences is not None:
            update_data["preferences"] = customer_data.preferences
        if customer_data.notes is not None:
            update_data["notes"] = customer_data.notes
        if customer_data.active is not None:
            update_data["active"] = customer_data.active
        
        # Update customer
        updated_customer = await customer_repo.update_by_id(customer_id, update_data, "customer_id")
        
        if not updated_customer:
            raise PlayParkException(
                error_code=ErrorCode.INTERNAL_ERROR,
                message="Failed to update customer"
            )
        
        return CustomerResponse(
            customer_id=updated_customer.customer_id,
            name=updated_customer.name,
            email=updated_customer.email,
            phone=updated_customer.phone,
            address=updated_customer.address,
            date_of_birth=updated_customer.date_of_birth,
            gender=updated_customer.gender,
            preferences=updated_customer.preferences,
            loyalty_points=updated_customer.loyalty_points,
            total_spent=updated_customer.total_spent,
            visit_count=updated_customer.visit_count,
            last_visit=updated_customer.last_visit,
            notes=updated_customer.notes,
            active=updated_customer.active,
            created_at=updated_customer.created_at,
            updated_at=updated_customer.updated_at
        )
        
    except PlayParkException:
        raise
    except Exception as e:
        raise PlayParkException(
            error_code=ErrorCode.INTERNAL_ERROR,
            message="Failed to update customer",
            details={"error": str(e)}
        )


@router.delete("/{customer_id}")
async def delete_customer(
    customer_id: str,
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Delete customer (soft delete by deactivating)"""
    try:
        customer_repo = CustomerRepository()
        
        # Get existing customer
        existing_customer = await customer_repo.get_by_field("customer_id", customer_id)
        if not existing_customer:
            raise PlayParkException(
                error_code=ErrorCode.NOT_FOUND,
                message="Customer not found",
                status_code=404
            )
        
        # Check tenant access
        if existing_customer.tenant_id != current_user.tenant_id:
            raise PlayParkException(
                error_code=ErrorCode.E_PERMISSION,
                message="Access denied",
                status_code=403
            )
        
        # Deactivate customer
        await customer_repo.deactivate(customer_id)
        
        return {"message": "Customer deactivated successfully"}
        
    except PlayParkException:
        raise
    except Exception as e:
        raise PlayParkException(
            error_code=ErrorCode.INTERNAL_ERROR,
            message="Failed to delete customer",
            details={"error": str(e)}
        )


@router.get("/top/spenders", response_model=List[CustomerResponse])
async def get_top_customers(
    limit: int = Query(10, ge=1, le=100),
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get top customers by spending"""
    try:
        customer_repo = CustomerRepository()
        
        top_customers = await customer_repo.get_top_customers(
            current_user.tenant_id, limit
        )
        
        return [
            CustomerResponse(
                customer_id=c.customer_id,
                name=c.name,
                email=c.email,
                phone=c.phone,
                address=c.address,
                date_of_birth=c.date_of_birth,
                gender=c.gender,
                preferences=c.preferences,
                loyalty_points=c.loyalty_points,
                total_spent=c.total_spent,
                visit_count=c.visit_count,
                last_visit=c.last_visit,
                notes=c.notes,
                active=c.active,
                created_at=c.created_at,
                updated_at=c.updated_at
            )
            for c in top_customers
        ]
        
    except Exception as e:
        raise PlayParkException(
            error_code=ErrorCode.INTERNAL_ERROR,
            message="Failed to get top customers",
            details={"error": str(e)}
        )
