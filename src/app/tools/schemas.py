"""
Pydantic schemas for AI Agent Tools.

Defines input/output schemas for all inventory management tools.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Any, Literal
from datetime import datetime


# ---------- Tool Response Schema ----------
class ToolResponse(BaseModel):
    """Standard response format for all tools."""
    success: bool
    data: Optional[Any] = None
    message: str
    gate_type: Literal["read_only", "soft_gate", "hard_gate"]

    class Config:
        from_attributes = True


# ---------- Read-Only Tool Inputs ----------
class QueryStockInput(BaseModel):
    """Input for query_inventory_stock tool."""
    product_sku: str = Field(..., description="Product SKU to check stock for")
    warehouse_name: Optional[str] = Field(None, description="Specific warehouse name (optional, omit for all warehouses)")


class QueryDetailsInput(BaseModel):
    """Input for query_inventory_details tool."""
    product_sku: str = Field(..., description="Product SKU to get details for")
    warehouse_name: Optional[str] = Field(None, description="Specific warehouse name (optional)")


class QueryLowStockInput(BaseModel):
    """Input for query_low_stock_items tool."""
    limit: int = Field(100, description="Maximum number of items to return")


class QueryMovementHistoryInput(BaseModel):
    """Input for query_movement_history tool."""
    product_sku: Optional[str] = Field(None, description="Product SKU to filter by")
    warehouse_name: Optional[str] = Field(None, description="Warehouse name to filter by")
    limit: int = Field(100, description="Maximum number of movements to return")


class QueryProductCatalogInput(BaseModel):
    """Input for query_product_catalog tool."""
    sku: Optional[str] = Field(None, description="Specific SKU to look up (optional, omit for list)")
    limit: int = Field(100, description="Maximum number of products to return if listing")


class QueryWarehouseCatalogInput(BaseModel):
    """Input for query_warehouse_catalog tool."""
    warehouse_name: Optional[str] = Field(None, description="Specific warehouse name to look up (optional)")
    limit: int = Field(100, description="Maximum number of warehouses to return if listing")


# ---------- Soft Gate Tool Inputs ----------
class CreateProductInput(BaseModel):
    """Input for create_product tool."""
    sku: str = Field(..., description="Unique SKU code for the product")
    name: str = Field(..., description="Product name")
    category: str = Field(..., description="Product category")
    unit_price: float = Field(..., description="Unit price in dollars")
    unit: str = Field(..., description="Unit of measure (e.g., 'case', 'unit', 'kg')")


class CreateWarehouseInput(BaseModel):
    """Input for create_warehouse tool."""
    name: str = Field(..., description="Warehouse name")
    location: str = Field(..., description="Physical address/location")
    region: str = Field(..., description="Geographic region")
    capacity: int = Field(..., description="Storage capacity in units")
    latitude: Optional[float] = Field(None, description="Latitude coordinate")
    longitude: Optional[float] = Field(None, description="Longitude coordinate")


class AdjustInboundInput(BaseModel):
    """Input for adjust_inventory_inbound tool."""
    product_sku: str = Field(..., description="Product SKU to receive")
    warehouse_name: str = Field(..., description="Destination warehouse")
    quantity: int = Field(..., gt=0, description="Quantity to receive (must be positive)")
    reference_number: Optional[str] = Field(None, description="PO or reference number")
    batch_number: Optional[str] = Field(None, description="Batch/lot number for tracking")


# ---------- Hard Gate Tool Inputs ----------
class ReportAnomalyInput(BaseModel):
    """Input for report_inventory_anomaly tool."""
    product_sku: str = Field(..., description="Product SKU affected")
    warehouse_name: str = Field(..., description="Warehouse where anomaly occurred")
    quantity: int = Field(..., gt=0, description="Quantity affected")
    reason: str = Field(..., description="Reason for anomaly (damage, theft, expired, etc.)")
    reference_number: Optional[str] = Field(None, description="Reference number for audit trail")


class AdjustOutboundInput(BaseModel):
    """Input for adjust_inventory_outbound tool."""
    product_sku: str = Field(..., description="Product SKU to ship")
    warehouse_name: str = Field(..., description="Source warehouse")
    quantity: int = Field(..., gt=0, description="Quantity to ship (must be positive)")
    reference_number: Optional[str] = Field(None, description="SO or shipment reference")
    batch_number: Optional[str] = Field(None, description="Specific batch to ship from (uses FIFO if not specified)")


class TransferInventoryInput(BaseModel):
    """Input for transfer_inventory tool."""
    product_sku: str = Field(..., description="Product SKU to transfer")
    source_warehouse: str = Field(..., description="Source warehouse name")
    destination_warehouse: str = Field(..., description="Destination warehouse name")
    quantity: int = Field(..., gt=0, description="Quantity to transfer")
    reference_number: Optional[str] = Field(None, description="Transfer order reference")
    batch_number: Optional[str] = Field(None, description="Specific batch to transfer (uses FIFO if not specified)")
