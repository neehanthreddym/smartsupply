'''
CRUD queries for inventory (Postgres) - read/write tables

1. ProductRepository.get_by_sku(sku)
2. WarehouseRepository.get_by_name(name)
3. InventoryRepository.get_stock(product_sku, warehouse_name)
4. MovementRepository.create_movement(...)
'''

from typing import Optional, List
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.inventory_models import Product, Warehouse, Inventory, Movement

# -----------------------
# Product Repository
# -----------------------
class ProductRepository:
    '''
    Handles all database operations related to products (Product catalog manager).
    * Find a product
    * List products
    * Create a new product
    * Update product price
    '''
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, product_id: int) -> Optional[Product]:
        '''Return a product by its ID, or None if not found.'''
        return self.db.query(Product).filter(Product.id == product_id).first()

    def get_by_sku(self, sku: str) -> Optional[Product]:
        """Return a product by its SKU code."""
        return self.db.query(Product).filter(Product.sku == sku).first()

    def list(self, limit: int = None) -> List[Product]:
        """Return a list of products up to the given limit."""
        query = self.db.query(Product)
        if limit is not None:
            query = query.limit(limit)
        return query.all()

    def create(self, sku: str, name: str, category: str, unit_price: float, unit: str) -> Product:
        """
        Create and save a new product.
        
        `flush()` is used so the product ID is available immediately.
        """
        product = Product(sku=sku, name=name, category=category, unit_price=unit_price, unit=unit)
        self.db.add(product)
        self.db.flush()  # gets product.id without committing
        return product

    def update_price(self, sku: str, unit_price: float) -> Optional[Product]:
        """Update the unit price of a product identified by SKU."""
        product = self.get_by_sku(sku)
        if not product:
            return None
        product.unit_price = unit_price
        self.db.flush()
        return product


# -----------------------
# Warehouse Repository
# -----------------------
class WarehouseRepository:
    """
    Handles database operations related to warehouse (warehouse directory).
    * Where products are stored
    * Their location, region, and capacity
    """
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, warehouse_id: str) -> Optional[Warehouse]:
        """Return a warehouse by its ID."""
        return self.db.query(Warehouse).filter(Warehouse.id == warehouse_id).first()

    def get_by_name(self, name: str) -> Optional[Warehouse]:
        """Return a warehouse by its name."""
        return self.db.query(Warehouse).filter(Warehouse.name == name).first()

    def list(self, limit: int = None) -> List[Warehouse]:
        """Return a list of warehouses."""
        query = self.db.query(Warehouse)
        if limit is not None:
            query = query.limit(limit)
        return query.all()

    def create(
        self,
        name: str,
        location: str,
        region: str,
        capacity: int,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
    ) -> Warehouse:
        """Create and save a new warehouse."""
        wh = Warehouse(
            name=name,
            location=location,
            region=region,
            capacity=capacity,
            latitude=latitude,
            longitude=longitude,
        )
        self.db.add(wh)
        self.db.flush()
        return wh


# -----------------------
# Inventory Repository
# -----------------------
class InventoryRepository:
    """Handles inventory records (product stock per warehouse)."""
    def __init__(self, db: Session):
        self.db = db
    
    def create_row(
        self,
        product: Product,
        warehouse: Warehouse,
        quantity: int = 0,
        reorder_level: Optional[int] = None,
        safety_stock: Optional[int] = None,
        batch_number: Optional[str] = None,
    ) -> Inventory:
        """
        Create a new inventory row for a product in a warehouse.
        Populates denormalized fields (names, SKU) for easier reading.
        """
        row = Inventory(
            product_id=product.id,
            warehouse_id=warehouse.id,
            product_sku=product.sku,
            product_name=product.name,
            warehouse_name=warehouse.name,
            quantity=int(quantity),
            reorder_level=reorder_level,
            safety_stock=safety_stock,
            batch_number=batch_number,
        )
        self.db.add(row)
        self.db.flush()
        return row

    def _get_product_and_warehouse(self, product_sku: str, warehouse_name: str) -> tuple[Optional[Product], Optional[Warehouse]]:
        product = self.db.query(Product).filter(Product.sku == product_sku).first()
        warehouse = self.db.query(Warehouse).filter(Warehouse.name == warehouse_name).first()
        return product, warehouse

    def get_row(self, product_sku: str, warehouse_name: str, batch_number: Optional[str] = None) -> Optional[Inventory]:
        """Return the inventory row for a product in a specific warehouse, optionally filtered by batch."""
        product, warehouse = self._get_product_and_warehouse(product_sku, warehouse_name)
        if not product or not warehouse:
            return None

        q = self.db.query(Inventory).filter(
            Inventory.product_id == product.id, 
            Inventory.warehouse_id == warehouse.id
        )
        
        if batch_number is not None:
             q = q.filter(Inventory.batch_number == batch_number)
        
        return q.first()

    def get_stock(self, product_sku: str, warehouse_name: str) -> Optional[int]:
        """Return the TOTAL stock quantity for a product in a warehouse (sum of all batches)."""
        rows = self.get_all_product_stock_in_warehouse(product_sku, warehouse_name)
        if not rows:
            return None
        return sum(r.quantity for r in rows)

    def get_all_product_stock_in_warehouse(self, product_sku: str, warehouse_name: str) -> List[Inventory]:
        """Return all batches for a product in a warehouse."""
        product, warehouse = self._get_product_and_warehouse(product_sku, warehouse_name)
        return (
            self.db.query(Inventory)
            .filter(Inventory.product_id == product.id, Inventory.warehouse_id == warehouse.id)
            .all()
        )

    def get_all_product_stock(self, product_sku: str) -> List[Inventory]:
        """Return all inventory rows for a product across all warehouses."""
        return (
            self.db.query(Inventory)
            .filter(Inventory.product_sku == product_sku)
            .all()
        )

    def set_stock(self, product_sku: str, warehouse_name: str, new_quantity: int, batch_number: Optional[str] = None) -> Optional[Inventory]:
        """
        Set inventory to an exact quantity for a specific batch.
        Auto-creates row if missing.
        Does NOT affect different batches.
        """
        row = self.get_row(product_sku, warehouse_name, batch_number)
        if not row:
            product, warehouse = self._get_product_and_warehouse(product_sku, warehouse_name)
            if not product or not warehouse:
                return None
            row = self.create_row(product, warehouse, quantity=new_quantity, batch_number=batch_number)
        else:
            row.quantity = int(new_quantity)
            if hasattr(row, "last_updated"):
                row.last_updated = datetime.utcnow()
            self.db.flush()
        return row

    def add_stock(self, product_sku: str, warehouse_name: str, delta: int, batch_number: Optional[str] = None) -> Optional[Inventory]:
        """
        Adds/removes inventory for a specific batch.
        Auto-creates row if missing (e.g. first inbound shipment).
        """
        product, warehouse = self._get_product_and_warehouse(product_sku, warehouse_name)
        if not product or not warehouse:
             return None

        row = self.get_row(product_sku, warehouse_name, batch_number)
        
        if not row:
            # Create new row
            row = self.create_row(product, warehouse, quantity=delta, batch_number=batch_number)
        else:
            row.quantity = int(row.quantity) + int(delta)
            if hasattr(row, "last_updated"):
                row.last_updated = datetime.utcnow()
            self.db.flush()
            
        return row

    def list_low_stock(self, limit: int = 100) -> List[Inventory]:
        """
        Return inventory items that are below safety or reorder levels.
        """
        q = self.db.query(Inventory)

        # only apply filters if fields exist in your model
        if hasattr(Inventory, "reorder_level") and hasattr(Inventory, "safety_stock"):
            q = q.filter((Inventory.quantity <= Inventory.reorder_level) | (Inventory.quantity <= Inventory.safety_stock))

        return q.limit(limit).all()

    def list_by_warehouse(self, warehouse_id: str, limit: int = 100) -> List[Inventory]:
        """Return all inventory rows for a warehouse."""
        return (
            self.db.query(Inventory)
            .filter(Inventory.warehouse_id == warehouse_id)
            .limit(limit)
            .all()
        )

# -----------------------
# Movement Repository
# -----------------------
class MovementRepository:
    """Records inventory movements for auditing and history."""
    def __init__(self, db: Session):
        self.db = db

    def create_movement(
        self,
        product_id: int,
        warehouse_id: int,
        movement_type: str,
        quantity: int,
        unit_price: Optional[float] = None,
        reference_number: Optional[str] = None,
        destination_warehouse_id: Optional[int] = None,
        destination_warehouse_name: Optional[str] = None,
        timestamp: Optional[datetime] = None,
        damage_reason: Optional[str] = None,
        before_quantity: Optional[int] = None,
        after_quantity: Optional[int] = None,
        batch_number: Optional[str] = None,
    ) -> Movement:
        """
        Create a movement record (inbound, outbound, transfer, adjustment).
        Automatically calculates total value if unit price is provided.
        """
        total_value = None
        if unit_price is not None:
            total_value = float(unit_price) * int(quantity)

        # distinct fetches for denormalized data
        prod = self.db.query(Product).get(product_id)
        wh = self.db.query(Warehouse).get(warehouse_id)
        
        dest_wh_name = destination_warehouse_name
        if not dest_wh_name and destination_warehouse_id:
             dest_wh = self.db.query(Warehouse).get(destination_warehouse_id)
             if dest_wh:
                 dest_wh_name = dest_wh.name

        m = Movement(
            product_id=product_id,
            product_sku=prod.sku if prod else None,
            product_name=prod.name if prod else None,
            warehouse_id=warehouse_id,
            warehouse_name=wh.name if wh else None,
            movement_type=movement_type,
            quantity=int(quantity),
            unit_price=unit_price,
            total_value=total_value,
            reference_number=reference_number,
            destination_warehouse_id=destination_warehouse_id,
            destination_warehouse_name=dest_wh_name,
            timestamp=timestamp or datetime.utcnow(),
            damage_reason=damage_reason,
            before_quantity=before_quantity,
            after_quantity=after_quantity,
            batch_number=batch_number,
        )
        self.db.add(m)
        self.db.flush()
        return m

    def list_recent(self, limit: int = 100) -> List[Movement]:
        """Return the most recent inventory movements."""
        return self.db.query(Movement).order_by(Movement.timestamp.desc()).limit(limit).all()
    
    def list_by_warehouse(self, warehouse_id: int, limit: int = 100) -> List[Movement]:
        """Return recent movements for a warehouse."""
        return (
            self.db.query(Movement)
            .filter(Movement.warehouse_id == warehouse_id)
            .order_by(Movement.timestamp.desc())
            .limit(limit)
            .all()
        )
    
    def list_by_product(self, product_id: int, limit: int = 100) -> List[Movement]:
        """Return recent movements for a product."""
        return (
            self.db.query(Movement)
            .filter(Movement.product_id == product_id)
            .order_by(Movement.timestamp.desc())
            .limit(limit)
            .all()
        )