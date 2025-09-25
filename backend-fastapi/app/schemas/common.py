"""
Common Schemas for Request/Response Envelopes
"""
from datetime import datetime
from typing import Optional, Any, Dict, List
from pydantic import BaseModel, Field


class ErrorDetail(BaseModel):
    """Error detail model"""
    
    field: Optional[str] = Field(default=None, description="Field name")
    message: str = Field(..., description="Error message")
    code: Optional[str] = Field(default=None, description="Error code")


class ErrorResponse(BaseModel):
    """Error response model"""
    
    error: str = Field(..., description="Error code")
    message: str = Field(..., description="Human readable error message")
    details: Optional[Dict[str, Any]] = Field(default=None, description="Additional error details")
    validation_errors: Optional[List[ErrorDetail]] = Field(default=None, description="Validation errors")


class SuccessResponse(BaseModel):
    """Success response model"""
    
    server_time: datetime = Field(default_factory=datetime.utcnow, description="Server timestamp")
    request_id: Optional[str] = Field(default=None, description="Request ID")
    data: Any = Field(..., description="Response data")


class PaginationParams(BaseModel):
    """Pagination parameters"""
    
    page: int = Field(default=1, ge=1, description="Page number")
    page_size: int = Field(default=50, ge=1, le=100, description="Page size")
    
    @property
    def offset(self) -> int:
        """Calculate offset from page and page_size"""
        return (self.page - 1) * self.page_size


class CursorPaginationParams(BaseModel):
    """Cursor-based pagination parameters"""
    
    limit: int = Field(default=50, ge=1, le=100, description="Result limit")
    cursor: Optional[str] = Field(default=None, description="Cursor for pagination")


class PaginationResponse(BaseModel):
    """Pagination response model"""
    
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Page size")
    total_pages: int = Field(..., description="Total number of pages")
    has_next: bool = Field(..., description="Has next page")
    has_prev: bool = Field(..., description="Has previous page")
    
    @classmethod
    def create(cls, total: int, page: int, page_size: int) -> "PaginationResponse":
        """Create pagination response"""
        total_pages = (total + page_size - 1) // page_size
        return cls(
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_prev=page > 1
        )


class CursorPaginationResponse(BaseModel):
    """Cursor-based pagination response model"""
    
    items: List[Any] = Field(..., description="Page items")
    next_cursor: Optional[str] = Field(default=None, description="Next cursor")
    has_more: bool = Field(..., description="Has more items")


class HealthCheckResponse(BaseModel):
    """Health check response model"""
    
    ok: bool = Field(..., description="Health status")
    status: str = Field(..., description="Status message")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Check timestamp")
    version: Optional[str] = Field(default=None, description="API version")
    environment: Optional[str] = Field(default=None, description="Environment")
    uptime: Optional[float] = Field(default=None, description="Uptime in seconds")


class MetricsResponse(BaseModel):
    """Metrics response model"""
    
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Metrics timestamp")
    metrics: Dict[str, Any] = Field(..., description="Metrics data")


class IdempotencyRequest(BaseModel):
    """Idempotency request model"""
    
    idempotency_key: Optional[str] = Field(default=None, description="Idempotency key")


class IdempotencyResponse(BaseModel):
    """Idempotency response model"""
    
    is_duplicate: bool = Field(..., description="Is duplicate request")
    original_response: Optional[Dict[str, Any]] = Field(default=None, description="Original response")


class BulkOperationRequest(BaseModel):
    """Bulk operation request model"""
    
    items: List[Dict[str, Any]] = Field(..., description="Items to process")
    operation: str = Field(..., description="Operation type")


class BulkOperationResponse(BaseModel):
    """Bulk operation response model"""
    
    processed: int = Field(..., description="Processed items count")
    successful: int = Field(..., description="Successful items count")
    failed: int = Field(..., description="Failed items count")
    errors: List[Dict[str, Any]] = Field(default_factory=list, description="Error details")


class FileUploadResponse(BaseModel):
    """File upload response model"""
    
    file_id: str = Field(..., description="Uploaded file ID")
    file_name: str = Field(..., description="File name")
    file_size: int = Field(..., description="File size in bytes")
    mime_type: str = Field(..., description="MIME type")
    url: Optional[str] = Field(default=None, description="File URL")


class FileDownloadRequest(BaseModel):
    """File download request model"""
    
    file_id: str = Field(..., description="File ID to download")
    format: Optional[str] = Field(default=None, description="Download format")


class SearchRequest(BaseModel):
    """Search request model"""
    
    query: str = Field(..., description="Search query")
    filters: Optional[Dict[str, Any]] = Field(default=None, description="Search filters")
    sort: Optional[str] = Field(default=None, description="Sort field")
    order: str = Field(default="asc", description="Sort order: asc or desc")
    limit: int = Field(default=50, ge=1, le=100, description="Result limit")


class SearchResponse(BaseModel):
    """Search response model"""
    
    query: str = Field(..., description="Search query")
    results: List[Any] = Field(..., description="Search results")
    total: int = Field(..., description="Total results count")
    took_ms: int = Field(..., description="Search time in milliseconds")


class BatchRequest(BaseModel):
    """Batch request model"""
    
    requests: List[Dict[str, Any]] = Field(..., description="Batch requests")
    parallel: bool = Field(default=False, description="Execute in parallel")


class BatchResponse(BaseModel):
    """Batch response model"""
    
    responses: List[Dict[str, Any]] = Field(..., description="Batch responses")
    executed_at: datetime = Field(default_factory=datetime.utcnow, description="Execution timestamp")
    duration_ms: int = Field(..., description="Execution duration in milliseconds")
