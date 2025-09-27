"""
Products Router - Complete CRUD API
"""
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field

from app.models.catalog import Product
from app.deps import CurrentUser, get_user_repository
from app.repositories.catalog import CatalogRepository
from app.utils.errors import PlayParkException, ErrorCode

router = APIRouter()


class ProductCreateRequest(BaseModel):
    """Product creation request"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    sku: Optional[str] = Field(None, max_length=100)
    price: float = Field(..., ge=0)
    cost: Optional[float] = Field(None, ge=0)
    category_id: Optional[str] = None
    active: bool = True
    settings: Dict[str, Any] = Field(default_factory=dict)


class ProductUpdateRequest(BaseModel):
    """Product update request"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    sku: Optional[str] = Field(None, max_length=100)
    price: Optional[float] = Field(None, ge=0)
    cost: Optional[float] = Field(None, ge=0)
    category_id: Optional[str] = None
    active: Optional[bool] = None
    settings: Optional[Dict[str, Any]] = None


class ProductResponse(BaseModel):
    """Product response"""
    product_id: str
    tenant_id: str
    store_id: str
    category_id: Optional[str]
    name: str
    description: Optional[str]
    sku: Optional[str]
    price: float
    cost: Optional[float]
    active: bool
    settings: Dict[str, Any]
    created_at: str
    updated_at: str


@router.get("/", response_model=Dict[str, Any])
async def get_products(
    store_id: Optional[str] = Query(None),
    category_id: Optional[str] = Query(None),
    active: Optional[bool] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user = CurrentUser,
    user_repository = Depends(get_user_repository)
) -> Dict[str, Any]:
    """Get products list with filtering"""
    
    try:
        # Use user's store_id if not provided
        if not store_id:
            store_id = current_user.store_id
        
        # Create catalog repository
        catalog_repo = CatalogRepository(user_repository.db)
        
        # Get products
        products = await catalog_repo.get_products(
            store_id=store_id,
            category_id=category_id,
            active=active,
            skip=skip,
            limit=limit
        )
        
        # Convert to response format
        product_list = []
        for product in products:
            product_list.append(ProductResponse(
                product_id=product.product_id,
                tenant_id=product.tenant_id,
                store_id=product.store_id,
                category_id=product.category_id,
                name=product.name,
                description=product.description,
                sku=product.sku,
                price=product.price,
                cost=product.cost,
                active=product.active,
                settings=product.settings,
                created_at=product.created_at.isoformat(),
                updated_at=product.updated_at.isoformat()
            ))
        
        return {
            "data": product_list,
            "total": len(product_list),
            "skip": skip,
            "limit": limit
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "E_INTERNAL_ERROR",
                "message": "Failed to retrieve products"
            }
        )


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: str,
    current_user = CurrentUser,
    user_repository = Depends(get_user_repository)
) -> ProductResponse:
    """Get product by ID"""
    
    try:
        catalog_repo = CatalogRepository(user_repository.db)
        product = await catalog_repo.get_product_by_id(product_id)
        
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": "E_PRODUCT_NOT_FOUND",
                    "message": "Product not found"
                }
            )
        
        return ProductResponse(
            product_id=product.product_id,
            tenant_id=product.tenant_id,
            store_id=product.store_id,
            category_id=product.category_id,
            name=product.name,
            description=product.description,
            sku=product.sku,
            price=product.price,
            cost=product.cost,
            active=product.active,
            settings=product.settings,
            created_at=product.created_at.isoformat(),
            updated_at=product.updated_at.isoformat()
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "E_INTERNAL_ERROR",
                "message": "Failed to retrieve product"
            }
        )


@router.post("/", response_model=ProductResponse)
async def create_product(
    request: ProductCreateRequest,
    current_user = CurrentUser,
    user_repository = Depends(get_user_repository)
) -> ProductResponse:
    """Create a new product"""
    
    try:
        catalog_repo = CatalogRepository(user_repository.db)
        
        # Generate product ID
        from datetime import datetime
        product_id = f"prod_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{current_user.employee_id}"
        
        # Create product
        product = Product(
            product_id=product_id,
            tenant_id=current_user.tenant_id,
            store_id=current_user.store_id,
            category_id=request.category_id,
            name=request.name,
            description=request.description,
            sku=request.sku,
            price=request.price,
            cost=request.cost,
            active=request.active,
            settings=request.settings
        )
        
        created_product = await catalog_repo.create_product(product)
        
        return ProductResponse(
            product_id=created_product.product_id,
            tenant_id=created_product.tenant_id,
            store_id=created_product.store_id,
            category_id=created_product.category_id,
            name=created_product.name,
            description=created_product.description,
            sku=created_product.sku,
            price=created_product.price,
            cost=created_product.cost,
            active=created_product.active,
            settings=created_product.settings,
            created_at=created_product.created_at.isoformat(),
            updated_at=created_product.updated_at.isoformat()
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "E_INTERNAL_ERROR",
                "message": "Failed to create product"
            }
        )


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: str,
    request: ProductUpdateRequest,
    current_user = CurrentUser,
    user_repository = Depends(get_user_repository)
) -> ProductResponse:
    """Update a product"""
    
    try:
        catalog_repo = CatalogRepository(user_repository.db)
        
        # Get existing product
        existing_product = await catalog_repo.get_product_by_id(product_id)
        if not existing_product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": "E_PRODUCT_NOT_FOUND",
                    "message": "Product not found"
                }
            )
        
        # Update fields
        update_data = request.dict(exclude_unset=True)
        updated_product = await catalog_repo.update_product(product_id, update_data)
        
        return ProductResponse(
            product_id=updated_product.product_id,
            tenant_id=updated_product.tenant_id,
            store_id=updated_product.store_id,
            category_id=updated_product.category_id,
            name=updated_product.name,
            description=updated_product.description,
            sku=updated_product.sku,
            price=updated_product.price,
            cost=updated_product.cost,
            active=updated_product.active,
            settings=updated_product.settings,
            created_at=updated_product.created_at.isoformat(),
            updated_at=updated_product.updated_at.isoformat()
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "E_INTERNAL_ERROR",
                "message": "Failed to update product"
            }
        )


@router.delete("/{product_id}")
async def delete_product(
    product_id: str,
    current_user = CurrentUser,
    user_repository = Depends(get_user_repository)
) -> Dict[str, Any]:
    """Delete a product"""
    
    try:
        catalog_repo = CatalogRepository(user_repository.db)
        
        # Check if product exists
        existing_product = await catalog_repo.get_product_by_id(product_id)
        if not existing_product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": "E_PRODUCT_NOT_FOUND",
                    "message": "Product not found"
                }
            )
        
        # Delete product
        await catalog_repo.delete_product(product_id)
        
        return {
            "success": True,
            "message": "Product deleted successfully"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "E_INTERNAL_ERROR",
                "message": "Failed to delete product"
            }
        )
