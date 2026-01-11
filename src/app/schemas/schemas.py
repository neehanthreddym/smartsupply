"""
Validates user input and serialize the output data for the inventory management system.
"""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class BaseResponse(BaseModel):
    class Config:
        orm_mode = True

class ProductResponse(BaseResponse):
    id: str
    sku: str
    name: str
    category: str
    unit_price: float
    unit: str

class WarehouseResponse(BaseResponse):
    id: str
    name: str
    location: Optional[str] = None
    capacity: Optional[int] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class InventoryResponse(BaseResponse):
    id: str
    product_id: str
    product_sku: str
    product_name: str
    warehouse_id: str
    warehouse_name: str
    quantity: int
    reorder_level: int
    safety_stock: int
    last_updated: datetime

class MovementResponse(BaseResponse):
    id: str
    product_id: str
    product_sku: str
    product_name: str
    warehouse_id: str
    warehouse_name: str
    movement_type: str
    quantity: int
    unit_price: float
    total_value: float
    timestamp: datetime
    reference_number: Optional[str] = None
    destination_warehouse_id: Optional[str] = None
    destination_warehouse_name: Optional[str] = None
    damage_reason: Optional[str] = None

class InventoryAdjustmentRequest(BaseModel):
    product_sku: str
    warehouse_name: str
    movement_type: str
    quantity: int

class InventoryTransferRequest(BaseModel):
    product_sku: str
    source_warehouse: str
    destination_warehouse: str
    quantity: int