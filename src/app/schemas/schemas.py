"""
Validates user input and serialize the output data for the inventory management system.
"""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class Base(BaseModel):
    class Config:
        from_attributes = True

# ---------- Inventory schemas ----------
class ProductResponse(Base):
    id: str
    sku: str
    name: str
    category: str
    unit_price: float
    unit: str

class WarehouseResponse(Base):
    id: str
    name: str
    location: Optional[str] = None
    capacity: Optional[int] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class InventoryResponse(Base):
    id: str
    product_id: str
    product_sku: str
    product_name: str
    warehouse_id: str
    warehouse_name: str
    quantity: int
    reorder_level: Optional[int] = None
    safety_stock: Optional[int] = None
    last_updated: Optional[datetime] = None
    batch_number: Optional[str] = None

class MovementResponse(Base):
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
    batch_number: Optional[str] = None

class InventoryAdjustmentRequest(Base):
    product_sku: str
    warehouse_name: str
    movement_type: str
    quantity: int
    reference_number: Optional[str] = None
    damage_reason: Optional[str] = None
    batch_number: Optional[str] = None

class InventoryTransferRequest(Base):
    product_sku: str
    source_warehouse: str
    destination_warehouse: str
    quantity: int
    reference_number: Optional[str] = None
    batch_number: Optional[str] = None

class ProductCreateRequest(Base):
    sku: str
    name: str
    category: str
    unit_price: float
    unit: str

class WarehouseCreateRequest(Base):
    name: str
    location: str
    region: str
    capacity: int
    latitude: Optional[float] = None
    longitude: Optional[float] = None

# ---------- Authentication schemas ----------
class Token(Base):
    access_token: str
    token_type: str

# ---------- User schemas ----------
class UserResponse(Base):
    id: str
    email: str
    full_name: Optional[str] = None
    role: str
    is_active: bool

class UserCreate(Base):
    email: str
    password: str
    full_name: Optional[str] = None