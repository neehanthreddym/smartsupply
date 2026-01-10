'''
Service Layer:
* enforce rules and business logic
* orchestrate multiple repositories in one transaction
* create movement logs whenever inventory changes
'''

from sqlalchemy.orm import Session
from app.repositories.inventory_repository import (
    ProductRepository, WarehouseRepository, InventoryRepository, MovementRepository
)

class CatalogService:
    """
    Service layer for catalog operations.

    Responsibilities:
    - List products
    - Get product by SKU
    - List warehouses
    - Get warehouse by name
    """
    def __init__(self, db: Session):
        self.products = ProductRepository(db)
        self.warehouses = WarehouseRepository(db)
    
    def list_products(self, limit: int = None):
        """Return a list of products up to the given limit. If limit is None, return all products."""
        return self.products.list(limit=limit)
    
    def get_product_by_sku(self, sku: str):
        """Return a product by its SKU code."""
        return self.products.get_by_sku(sku=sku)
    
    def list_warehouses(self, limit: int = None):
        """Return a list of warehouses up to the given limit. If limit is None, return all warehouses."""
        return self.warehouses.list(limit=limit)
    
    def get_warehouse_by_id(self, id: int):
        """Return a warehouse by its ID."""
        return self.warehouses.get_by_id(id=id)

class InventoryService:
    """
    Service layer for inventory operations.

    This class contains business logic for:
    - Reading stock levels
    - Moving stock in/out
    - Transferring stock between warehouses

    It coordinates multiple repositories and controls transactions.
    """
    def __init__(self, db: Session):
        """
        Initialize the service with a database session.

        All repository operations performed by this service
        share the same transaction context.
        """
        self.db = db
        self.products = ProductRepository(db)
        self.warehouses = WarehouseRepository(db)
        self.inventory = InventoryRepository(db)
        self.movements = MovementRepository(db)

    def get_stock(self, product_sku: str, warehouse_name: str) -> int:
        """
        Return the current stock quantity for a product in a warehouse.

        Raises:
            ValueError: If the product, warehouse, or inventory row does not exist.
        """
        qty = self.inventory.get_stock(product_sku, warehouse_name)
        if qty is None:
            raise ValueError("Product or warehouse not found (or inventory record missing).")
        return qty

    def move_stock(self, product_sku: str, warehouse_name: str, movement_type: str, quantity: int) -> int:
        """
        Move stock in or out of a warehouse and record the movement.

        Supported movement types:
            - "inbound"  (increase stock)
            - "outbound" (decrease stock)
            - "damage"   (decrease stock due to damage)
            - "adjust"   (manual correction)

        Args:
            product_sku: SKU of the product.
            warehouse_name: Name of the warehouse.
            movement_type: Type of inventory movement.
            quantity: Positive quantity to move.

        Returns:
            The updated stock quantity.

        Raises:
            ValueError: If inputs are invalid or stock would go negative.
        """
        if quantity <= 0:
            raise ValueError("quantity must be > 0")

        product = self.products.get_by_sku(product_sku)
        wh = self.warehouses.get_by_name(warehouse_name)
        if not product or not wh:
            raise ValueError("Invalid product SKU or warehouse name")

        delta = quantity if movement_type == "inbound" else -quantity

        row = self.inventory.add_stock(product_sku, warehouse_name, delta)
        if not row:
            raise ValueError("Inventory record not found.")

        if row.quantity < 0:
            raise ValueError("Insufficient stock (cannot go negative).")

        # log movement (audit trail)
        self.movements.create_movement(
            product_id=product.id,
            warehouse_id=wh.id,
            movement_type=movement_type,
            quantity=quantity,
            unit_price=getattr(product, "unit_price", None),
        )

        # Commit once
        self.db.commit()
        return row.quantity

    def transfer_stock(self, product_sku: str, source_wh: str, dest_wh: str, quantity: int) -> dict:
        """
        Transfer stock from one warehouse to another.

        This operation:
        - Subtracts stock from the source warehouse
        - Adds stock to the destination warehouse
        - Records a transfer movement

        Args:
            product_sku: SKU of the product being transferred.
            source_wh: Source warehouse name.
            dest_wh: Destination warehouse name.
            quantity: Positive quantity to transfer.

        Returns:
            A dictionary with updated quantities:
            {
                "source_qty": int,
                "dest_qty": int
            }

        Raises:
            ValueError: If warehouses are invalid, identical, or stock is insufficient.
        """
        if quantity <= 0:
            raise ValueError("quantity must be > 0")
        if source_wh == dest_wh:
            raise ValueError("source and destination cannot be the same")

        product = self.products.get_by_sku(product_sku)
        src = self.warehouses.get_by_name(source_wh)
        dst = self.warehouses.get_by_name(dest_wh)
        if not product or not src or not dst:
            raise ValueError("Invalid product/warehouse")

        # subtract from source
        src_row = self.inventory.add_stock(product_sku, source_wh, -quantity)
        if not src_row or src_row.quantity < 0:
            raise ValueError("Insufficient stock in source warehouse")

        # add to destination
        dst_row = self.inventory.add_stock(product_sku, dest_wh, quantity)
        if not dst_row:
            raise ValueError("Destination inventory row missing")

        # log transfer
        self.movements.create_movement(
            product_id=product.id,
            warehouse_id=src.id,
            movement_type="transfer",
            quantity=quantity,
            unit_price=getattr(product, "unit_price", None),
            destination_warehouse_id=dst.id,
        )

        self.db.commit()
        return {"source_qty": src_row.quantity, "dest_qty": dst_row.quantity}