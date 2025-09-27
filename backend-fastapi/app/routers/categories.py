"""
Categories Router - Complete CRUD API
"""
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field

from app.models.catalog import Category
from app.deps import CurrentUser, get_user_repository
from app.repositories.catalog import CatalogRepository

router = APIRouter()


class CategoryCreateRequest(BaseModel):
    """Category creation request"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    parent_id: Optional[str] = None
    sort_order: int = Field(0, ge=0)
    active: bool = True
    settings: Dict[str, Any] = Field(default_factory=dict)


class CategoryUpdateRequest(BaseModel):
    """Category update request"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    parent_id: Optional[str] = None
    sort_order: Optional[int] = Field(None, ge=0)
    active: Optional[bool] = None
    settings: Optional[Dict[str, Any]] = None


class CategoryResponse(BaseModel):
    """Category response"""
    category_id: str
    tenant_id: str
    store_id: str
    name: str
    description: Optional[str]
    parent_id: Optional[str]
    sort_order: int
    active: bool
    settings: Dict[str, Any]
    created_at: str
    updated_at: str


@router.get("/", response_model=Dict[str, Any])
async def get_categories(
    store_id: Optional[str] = Query(None),
    parent_id: Optional[str] = Query(None),
    active: Optional[bool] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user = CurrentUser,
    user_repository = Depends(get_user_repository)
) -> Dict[str, Any]:
    """Get categories list with filtering"""
    
    try:
        # Use user's store_id if not provided
        if not store_id:
            store_id = current_user.store_id
        
        # Create catalog repository
        catalog_repo = CatalogRepository(user_repository.db)
        
        # Get categories
        categories = await catalog_repo.get_categories(
            store_id=store_id,
            parent_id=parent_id,
            active=active,
            skip=skip,
            limit=limit
        )
        
        # Convert to response format
        category_list = []
        for category in categories:
            category_list.append(CategoryResponse(
                category_id=category.category_id,
                tenant_id=category.tenant_id,
                store_id=category.store_id,
                name=category.name,
                description=category.description,
                parent_id=category.parent_id,
                sort_order=category.sort_order,
                active=category.active,
                settings=category.settings,
                created_at=category.created_at.isoformat(),
                updated_at=category.updated_at.isoformat()
            ))
        
        return {
            "data": category_list,
            "total": len(category_list),
            "skip": skip,
            "limit": limit
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "E_INTERNAL_ERROR",
                "message": "Failed to retrieve categories"
            }
        )


@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(
    category_id: str,
    current_user = CurrentUser,
    user_repository = Depends(get_user_repository)
) -> CategoryResponse:
    """Get category by ID"""
    
    try:
        catalog_repo = CatalogRepository(user_repository.db)
        category = await catalog_repo.get_category_by_id(category_id)
        
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": "E_CATEGORY_NOT_FOUND",
                    "message": "Category not found"
                }
            )
        
        return CategoryResponse(
            category_id=category.category_id,
            tenant_id=category.tenant_id,
            store_id=category.store_id,
            name=category.name,
            description=category.description,
            parent_id=category.parent_id,
            sort_order=category.sort_order,
            active=category.active,
            settings=category.settings,
            created_at=category.created_at.isoformat(),
            updated_at=category.updated_at.isoformat()
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "E_INTERNAL_ERROR",
                "message": "Failed to retrieve category"
            }
        )


@router.post("/", response_model=CategoryResponse)
async def create_category(
    request: CategoryCreateRequest,
    current_user = CurrentUser,
    user_repository = Depends(get_user_repository)
) -> CategoryResponse:
    """Create a new category"""
    
    try:
        catalog_repo = CatalogRepository(user_repository.db)
        
        # Generate category ID
        from datetime import datetime
        category_id = f"cat_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{current_user.employee_id}"
        
        # Create category
        category = Category(
            category_id=category_id,
            tenant_id=current_user.tenant_id,
            store_id=current_user.store_id,
            name=request.name,
            description=request.description,
            parent_id=request.parent_id,
            sort_order=request.sort_order,
            active=request.active,
            settings=request.settings
        )
        
        created_category = await catalog_repo.create_category(category)
        
        return CategoryResponse(
            category_id=created_category.category_id,
            tenant_id=created_category.tenant_id,
            store_id=created_category.store_id,
            name=created_category.name,
            description=created_category.description,
            parent_id=created_category.parent_id,
            sort_order=created_category.sort_order,
            active=created_category.active,
            settings=created_category.settings,
            created_at=created_category.created_at.isoformat(),
            updated_at=created_category.updated_at.isoformat()
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "E_INTERNAL_ERROR",
                "message": "Failed to create category"
            }
        )


@router.put("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: str,
    request: CategoryUpdateRequest,
    current_user = CurrentUser,
    user_repository = Depends(get_user_repository)
) -> CategoryResponse:
    """Update a category"""
    
    try:
        catalog_repo = CatalogRepository(user_repository.db)
        
        # Get existing category
        existing_category = await catalog_repo.get_category_by_id(category_id)
        if not existing_category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": "E_CATEGORY_NOT_FOUND",
                    "message": "Category not found"
                }
            )
        
        # Update fields
        update_data = request.dict(exclude_unset=True)
        updated_category = await catalog_repo.update_category(category_id, update_data)
        
        return CategoryResponse(
            category_id=updated_category.category_id,
            tenant_id=updated_category.tenant_id,
            store_id=updated_category.store_id,
            name=updated_category.name,
            description=updated_category.description,
            parent_id=updated_category.parent_id,
            sort_order=updated_category.sort_order,
            active=updated_category.active,
            settings=updated_category.settings,
            created_at=updated_category.created_at.isoformat(),
            updated_at=updated_category.updated_at.isoformat()
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "E_INTERNAL_ERROR",
                "message": "Failed to update category"
            }
        )


@router.delete("/{category_id}")
async def delete_category(
    category_id: str,
    current_user = CurrentUser,
    user_repository = Depends(get_user_repository)
) -> Dict[str, Any]:
    """Delete a category"""
    
    try:
        catalog_repo = CatalogRepository(user_repository.db)
        
        # Check if category exists
        existing_category = await catalog_repo.get_category_by_id(category_id)
        if not existing_category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": "E_CATEGORY_NOT_FOUND",
                    "message": "Category not found"
                }
            )
        
        # Delete category
        await catalog_repo.delete_category(category_id)
        
        return {
            "success": True,
            "message": "Category deleted successfully"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "E_INTERNAL_ERROR",
                "message": "Failed to delete category"
            }
        )
