"""
Provider Models (Phase 6 - Advanced Reporting & Analytics)
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum

from .core import BaseDocument


class ReportType(str, Enum):
    """Report types"""
    DASHBOARD = "dashboard"
    REPORT = "report"
    ANALYTICS = "analytics"


class ReportCategory(str, Enum):
    """Report categories"""
    FLEET = "fleet"
    SALES = "sales"
    PERFORMANCE = "performance"
    ALERTS = "alerts"
    USAGE = "usage"
    CUSTOM = "custom"


class WidgetType(str, Enum):
    """Widget types"""
    METRIC = "metric"
    CHART = "chart"
    TABLE = "table"
    ALERT = "alert"
    MAP = "map"


class ChartType(str, Enum):
    """Chart types"""
    LINE = "line"
    BAR = "bar"
    PIE = "pie"
    AREA = "area"
    SCATTER = "scatter"


class GenerationStatus(str, Enum):
    """Report generation status"""
    PENDING = "pending"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"


class ExportFormat(str, Enum):
    """Export formats"""
    CSV = "csv"
    EXCEL = "excel"
    PDF = "pdf"
    JSON = "json"


class TrendType(str, Enum):
    """Trend types"""
    INCREASING = "increasing"
    DECREASING = "decreasing"
    STABLE = "stable"
    INSUFFICIENT_DATA = "insufficient_data"


class InsightType(str, Enum):
    """Insight types"""
    TRENDING_UP = "trending_up"
    TRENDING_DOWN = "trending_down"
    HIGH_VALUE = "high_value"
    LOW_VALUE = "low_value"
    ANOMALY = "anomaly"


class ReportTemplate(BaseDocument):
    """Report template model"""
    
    template_id: str = Field(..., description="Unique template identifier")
    name: str = Field(..., description="Template name")
    description: Optional[str] = Field(default=None, description="Template description")
    category: ReportCategory = Field(..., description="Template category")
    type: ReportType = Field(..., description="Template type")
    scope: str = Field(default="global", description="Template scope")
    config: Dict[str, Any] = Field(..., description="Template configuration")
    permissions: Dict[str, List[str]] = Field(default_factory=dict, description="Template permissions")
    created_by: str = Field(..., description="Creator user ID")
    updated_by: Optional[str] = Field(default=None, description="Last updater user ID")
    is_active: bool = Field(default=True, description="Template active status")
    
    class Config:
        collection = "report_templates"


class ReportInstance(BaseDocument):
    """Report instance model"""
    
    instance_id: str = Field(..., description="Unique instance identifier")
    template_id: str = Field(..., description="Template ID")
    generated_by: str = Field(..., description="Generator user ID")
    status: GenerationStatus = Field(default=GenerationStatus.PENDING, description="Generation status")
    config: Dict[str, Any] = Field(default_factory=dict, description="Generation configuration")
    data: Optional[Dict[str, Any]] = Field(default=None, description="Generated data")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Generation metadata")
    started_at: Optional[datetime] = Field(default=None, description="Generation start time")
    completed_at: Optional[datetime] = Field(default=None, description="Generation completion time")
    error_message: Optional[str] = Field(default=None, description="Error message")
    
    class Config:
        collection = "report_instances"


class DashboardWidget(BaseDocument):
    """Dashboard widget model"""
    
    widget_id: str = Field(..., description="Unique widget identifier")
    name: str = Field(..., description="Widget name")
    type: WidgetType = Field(..., description="Widget type")
    title: str = Field(..., description="Widget title")
    category: ReportCategory = Field(..., description="Widget category")
    config: Dict[str, Any] = Field(..., description="Widget configuration")
    data_source: Dict[str, Any] = Field(..., description="Widget data source")
    created_by: str = Field(..., description="Creator user ID")
    updated_by: Optional[str] = Field(default=None, description="Last updater user ID")
    usage_count: int = Field(default=0, description="Usage count")
    is_active: bool = Field(default=True, description="Widget active status")
    
    class Config:
        collection = "dashboard_widgets"


class ExportFile(BaseDocument):
    """Export file model"""
    
    file_id: str = Field(..., description="Unique file identifier")
    instance_id: str = Field(..., description="Report instance ID")
    format: ExportFormat = Field(..., description="Export format")
    file_path: str = Field(..., description="File path")
    file_name: str = Field(..., description="File name")
    mime_type: str = Field(..., description="MIME type")
    size: int = Field(..., description="File size in bytes")
    download_count: int = Field(default=0, description="Download count")
    expires_at: datetime = Field(..., description="Expiration date")
    created_by: str = Field(..., description="Creator user ID")
    
    class Config:
        collection = "export_files"


class AnalyticsData(BaseModel):
    """Analytics data model"""
    
    template_id: str = Field(..., description="Template ID")
    period: str = Field(..., description="Analytics period")
    trends: Dict[str, TrendType] = Field(default_factory=dict, description="Trend analysis")
    forecasts: Dict[str, List[float]] = Field(default_factory=dict, description="Forecast data")
    insights: List[Dict[str, Any]] = Field(default_factory=list, description="Generated insights")
    metrics: Dict[str, Any] = Field(default_factory=dict, description="Analytics metrics")
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="Generation timestamp")


class AnalyticsInsight(BaseModel):
    """Analytics insight model"""
    
    type: InsightType = Field(..., description="Insight type")
    metric: str = Field(..., description="Metric name")
    value: Optional[float] = Field(default=None, description="Metric value")
    message: str = Field(..., description="Insight message")
    confidence: float = Field(default=0.0, ge=0.0, le=1.0, description="Confidence score")


class ReportTemplateCreate(BaseModel):
    """Report template creation model"""
    
    name: str = Field(..., description="Template name")
    description: Optional[str] = Field(default=None, description="Template description")
    category: ReportCategory = Field(..., description="Template category")
    type: ReportType = Field(..., description="Template type")
    scope: str = Field(default="global", description="Template scope")
    config: Dict[str, Any] = Field(..., description="Template configuration")
    permissions: Dict[str, List[str]] = Field(default_factory=dict, description="Template permissions")


class ReportTemplateUpdate(BaseModel):
    """Report template update model"""
    
    name: Optional[str] = Field(default=None, description="Template name")
    description: Optional[str] = Field(default=None, description="Template description")
    config: Optional[Dict[str, Any]] = Field(default=None, description="Template configuration")
    permissions: Optional[Dict[str, List[str]]] = Field(default=None, description="Template permissions")
    is_active: Optional[bool] = Field(default=None, description="Template active status")


class DashboardWidgetCreate(BaseModel):
    """Dashboard widget creation model"""
    
    name: str = Field(..., description="Widget name")
    type: WidgetType = Field(..., description="Widget type")
    title: str = Field(..., description="Widget title")
    category: ReportCategory = Field(..., description="Widget category")
    config: Dict[str, Any] = Field(..., description="Widget configuration")
    data_source: Dict[str, Any] = Field(..., description="Widget data source")


class ReportGenerationRequest(BaseModel):
    """Report generation request model"""
    
    config: Dict[str, Any] = Field(default_factory=dict, description="Generation configuration")
    filters: Dict[str, Any] = Field(default_factory=dict, description="Data filters")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Template parameters")


class ExportRequest(BaseModel):
    """Export request model"""
    
    format: ExportFormat = Field(..., description="Export format")
    template: Optional[str] = Field(default=None, description="Export template")
    include_charts: bool = Field(default=True, description="Include charts flag")
    include_data: bool = Field(default=True, description="Include data flag")
    compression: bool = Field(default=False, description="Compression flag")


class ReportingStatistics(BaseModel):
    """Reporting statistics model"""
    
    templates: Dict[str, int] = Field(..., description="Template statistics")
    reports: Dict[str, int] = Field(..., description="Report statistics")
    exports: Dict[str, int] = Field(..., description="Export statistics")
    widgets: Dict[str, int] = Field(..., description="Widget statistics")
    performance: Dict[str, Any] = Field(..., description="Performance metrics")
