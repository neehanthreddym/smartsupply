"""SQLAlchemy models for PostgreSQL"""

from app.database.postgres import Base
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid

class Product(Base):
    __tablename__ = "products"

    # primary key as UUID string
    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    sku = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    category = Column(String)
    unit_price = Column(Float)
    unit = Column(String)

    # Relationships
    inventory_items = relationship("Inventory", back_populates="product")
    movements = relationship("Movement", back_populates="product")

class Inventory(Base):
    __tablename__ = "inventory"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    product_id = Column(String, ForeignKey("products.id"), nullable=False)
    product_sku = Column(String)
    product_name = Column(String)
    warehouse_id = Column(String, ForeignKey("warehouses.id"), nullable=False)
    warehouse_name = Column(String)
    quantity = Column(Integer)
    reorder_level = Column(Integer)
    safety_stock = Column(Integer)
    last_updated = Column(DateTime, 
                          default=lambda: datetime.now(timezone.utc),
                          onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    product = relationship("Product", back_populates="inventory_items")
    warehouse = relationship("Warehouse", back_populates="inventory_items")

class Movement(Base):
    __tablename__ = "inventory_movements"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    product_id = Column(String, ForeignKey("products.id"), nullable=False)
    product_sku = Column(String)
    product_name = Column(String)
    warehouse_id = Column(String, ForeignKey("warehouses.id"), nullable=False)
    warehouse_name = Column(String)
    movement_type = Column(String)
    quantity = Column(Integer)
    unit_price = Column(Float)
    total_value = Column(Float)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    reference_number = Column(String)
    destination_warehouse_id = Column(String, ForeignKey('warehouses.id'), nullable=True)
    destination_warehouse_name = Column(String, nullable=True)
    damage_reason = Column(String, nullable=True)

    # Relationships
    product = relationship("Product", back_populates="movements")
    warehouse = relationship(
        "Warehouse", 
        back_populates="movements", 
        foreign_keys=[warehouse_id]
    )
    destination_warehouse = relationship(
        "Warehouse",
        back_populates="destination_movements",
        foreign_keys=[destination_warehouse_id]
    )

class Warehouse(Base):
    __tablename__ = "warehouses"
    
    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    location = Column(String)
    region = Column(String)
    capacity = Column(Integer)
    latitude = Column(Float)
    longitude = Column(Float)

    # Relationships
    inventory_items = relationship("Inventory", back_populates="warehouse")
    movements = relationship(
        "Movement", 
        back_populates="warehouse", 
        foreign_keys=[Movement.warehouse_id]
    )
    destination_movements = relationship(
        "Movement",
        back_populates="destination_warehouse",
        foreign_keys=[Movement.destination_warehouse_id]
    )