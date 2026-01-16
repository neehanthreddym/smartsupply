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
from typing import Optional
from datetime import datetime
from app.services.log_service import LogService

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

    def create_product(self, sku: str, name: str, category: str, unit_price: float, unit: str):
        """Create a new product if it doesn't already exist."""
        existing = self.products.get_by_sku(sku)
        if existing:
            raise ValueError(f"Product with SKU '{sku}' already exists.")
        
        new_product = self.products.create(sku=sku, name=name, category=category, unit_price=unit_price, unit=unit)
        
        LogService.log_catalog_event(
            entity_type="product",
            entity_id=sku,
            action="create",
            details={"name": name, "category": category, "unit_price": unit_price, "unit": unit}
        )
        return new_product
    
    def list_warehouses(self, limit: int = None):
        """Return a list of warehouses up to the given limit. If limit is None, return all warehouses."""
        return self.warehouses.list(limit=limit)
    
    def get_warehouse_by_id(self, warehouse_id: str):
        """Return a warehouse by its ID."""
        return self.warehouses.get_by_id(warehouse_id=warehouse_id)

    def create_warehouse(self, name: str, location: str, region: str, capacity: int, latitude: Optional[float] = None, longitude: Optional[float] = None):
        """Create a new warehouse if it doesn't already exist."""
        existing = self.warehouses.get_by_name(name)
        if existing:
            raise ValueError(f"Warehouse with name '{name}' already exists at {existing.region} {existing.location}.")
        
        new_wh = self.warehouses.create(name=name, location=location, region=region, capacity=capacity, latitude=latitude, longitude=longitude)

        LogService.log_catalog_event(
            entity_type="warehouse",
            entity_id=name,
            action="create",
            details={"location": location, "region": region, "capacity": capacity}
        )
        return new_wh

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

    def get_stock(self, product_sku: str, warehouse_name: str = None) -> int:
        """
        Return the current stock quantity for a product.
        If warehouse_name is None, returns total stock across all warehouses.

        Raises:
            ValueError: If the product or warehouse does not exist.
        """
        if warehouse_name:
            qty = self.inventory.get_stock(product_sku, warehouse_name)
            if qty is None:
                raise ValueError("Product or warehouse not found (or inventory record missing).")
            return qty
        
        # Aggregate across all warehouses
        rows = self.inventory.get_all_product_stock(product_sku)
        # Verify product existence if no rows found, to provide helpful error
        if not rows:
            product = self.products.get_by_sku(product_sku)
            if not product:
                raise ValueError(f"Product {product_sku} not found.")
            return 0
            
        return sum(row.quantity for row in rows)

    def get_inventory_record(self, product_sku: str, warehouse_name: str = None):
        """
        Return the full inventory record object(s).
        If warehouse_name is set, returns a single Inventory object.
        If warehouse_name is None, returns a list of Inventory objects.
        """
        if warehouse_name:
            # Return all batches for this warehouse so user sees breakdown
            rows = self.inventory.get_all_product_stock_in_warehouse(product_sku, warehouse_name)
            if not rows:
                raise ValueError("Inventory record not found.")
            return rows
        
        # Return all rows for this product
        rows = self.inventory.get_all_product_stock(product_sku)
        if not rows:
            # Check if product exists to give better error, or just return empty list
            # Here, if product exists but no stock, empty list is valid.
            # If product doesn't exist, we probably want 404 (ValueError).
            product = self.products.get_by_sku(product_sku)
            if not product:
                raise ValueError(f"Product {product_sku} not found.")
            return []
            
        return rows

    def move_stock(self, 
        product_sku: str, 
        warehouse_name: str, 
        movement_type: str, 
        quantity: int, 
        reference_number: Optional[str] = None, 
        damage_reason: Optional[str] = None,
        batch_number: Optional[str] = None
    ):
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
        if not product:
            raise ValueError(f"Product SKU '{product_sku}' not found in Catalog. Please create the Product  before receiving stock.")

        wh = self.warehouses.get_by_name(warehouse_name)
        if not wh:
             raise ValueError(f"Warehouse '{warehouse_name}' not found.")

        if movement_type == "inbound":
             # INBOUND: Add to specific batch (or create new)
             row = self.inventory.add_stock(product_sku, warehouse_name, quantity, batch_number=batch_number)
             if not row:
                 raise ValueError("Failed to create inventory record.")
             
             # Log inbound movement
             m = self.movements.create_movement(
                 product_id=product.id,
                 warehouse_id=wh.id,
                 movement_type=movement_type,
                 quantity=quantity,
                 unit_price=getattr(product, "unit_price", None),
                 reference_number=reference_number,
                 damage_reason=damage_reason,
                 before_quantity=int(row.quantity) - quantity,
                 after_quantity=int(row.quantity),
                 batch_number=batch_number,
             )
             self.db.commit()
             self.db.refresh(m)

             LogService.log_inventory_event(
                 action_type=movement_type,
                 product_sku=product_sku,
                 quantity_change=quantity,
                 before_quantity=m.before_quantity,
                 after_quantity=m.after_quantity,
                 warehouse_name=warehouse_name,
                 reference_id=str(m.id)
             )
             return m

        else:
            # OUTBOUND / DAMAGE / ADJUST
            # Determine Quantity to Remove
            qty_to_remove = quantity
            
            # Check Total Stock First
            current_total = self.inventory.get_stock(product_sku, warehouse_name) or 0
            if current_total < qty_to_remove:
                 raise ValueError(f"Insufficient total stock. Available: {current_total}, Requested: {qty_to_remove}")

            # Deduct logic
            movements_created = []
            
            if batch_number:
                # Targeted Deduction
                row = self.inventory.add_stock(product_sku, warehouse_name, -qty_to_remove, batch_number=batch_number)
                # row.quantity is already updated
                if not row or row.quantity < 0:
                     # This might happen if batch specific stock is low even if total is high
                     raise ValueError("Insufficient stock in specified batch.")
                
                m = self.movements.create_movement(
                    product_id=product.id,
                    warehouse_id=wh.id,
                    movement_type=movement_type,
                    quantity=qty_to_remove,
                    unit_price=getattr(product, "unit_price", None),
                    reference_number=reference_number,
                    damage_reason=damage_reason,
                    before_quantity=int(row.quantity) + qty_to_remove,
                    after_quantity=int(row.quantity),
                    batch_number=batch_number,
                )
                movements_created.append(m)

                LogService.log_inventory_event(
                    action_type=movement_type,
                    product_sku=product_sku,
                    quantity_change=-qty_to_remove,
                    before_quantity=m.before_quantity,
                    after_quantity=m.after_quantity,
                    warehouse_name=warehouse_name,
                    reference_id=str(m.id)
                )

            else:
                # FIFO Deduction
                rows = self.inventory.get_all_product_stock_in_warehouse(product_sku, warehouse_name)
                # Sort by last_updated as proxy for First-In (Oldest updated)
                # Ideally we want Creation Time. Assuming older IDs or update times.
                # Assume list is returned in manageable order.
                rows.sort(key=lambda x: x.last_updated or datetime.min)
                
                remaining = qty_to_remove
                
                for r in rows:
                    if remaining <= 0:
                        break
                    if r.quantity <= 0:
                        continue
                        
                    deduct = min(r.quantity, remaining)
                    
                    # Deduct from this batch
                    updated_row = self.inventory.add_stock(product_sku, warehouse_name, -deduct, batch_number=r.batch_number)
                    
                    # Log movement
                    m = self.movements.create_movement(
                        product_id=product.id,
                        warehouse_id=wh.id,
                        movement_type=movement_type,
                        quantity=deduct,
                        unit_price=getattr(product, "unit_price", None),
                        reference_number=reference_number,
                        damage_reason=damage_reason,
                        before_quantity=int(updated_row.quantity) + deduct,
                        after_quantity=int(updated_row.quantity),
                        batch_number=r.batch_number,
                    )
                    movements_created.append(m)
                    
                    LogService.log_inventory_event(
                        action_type=movement_type,
                        product_sku=product_sku,
                        quantity_change=-deduct,
                        before_quantity=m.before_quantity,
                        after_quantity=m.after_quantity,
                        warehouse_name=warehouse_name,
                        reference_id=str(m.id)
                    )
                    
                    remaining -= deduct
                
                if remaining > 0:
                     # Should have been caught by total check, but just in case
                     raise ValueError("Error during FIFO deduction: Could not allocate full quantity.")

            self.db.commit()
            # return the LAST created movement to satisfy signature, or the main one
            if movements_created:
                last_m = movements_created[-1]
                self.db.refresh(last_m)
                return last_m
            else:
                 raise ValueError("No movements created.")

    def transfer_stock(self, 
        product_sku: str, 
        source_wh: str, 
        dest_wh: str, 
        quantity: int, 
        reference_number: Optional[str] = None,
        batch_number: Optional[str] = None
    ):
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

        # Check Total Stock
        current_total = self.inventory.get_stock(product_sku, source_wh) or 0
        if current_total < quantity:
             raise ValueError(f"Insufficient total source stock. Available: {current_total}")

        # Determine Batches to Move
        batches_to_move = [] # List of (batch_number, qty)
        
        if batch_number:
             # Targeted Transfer
             # Verify batch exists and has stock? add_stock will fail if we go negative, but let's trust it.
             batches_to_move.append((batch_number, quantity))
        else:
             # FIFO Transfer
             rows = self.inventory.get_all_product_stock_in_warehouse(product_sku, source_wh)
             rows.sort(key=lambda x: x.last_updated or datetime.min)
             
             remaining = quantity
             for r in rows:
                 if remaining <= 0: break
                 if r.quantity <= 0: continue
                 
                 deduct = min(r.quantity, remaining)
                 batches_to_move.append((r.batch_number, deduct))
                 remaining -= deduct
                 
             if remaining > 0:
                  raise ValueError("Error during FIFO transfer: Could not allocate full quantity.")

        # Execute Transfer per Batch
        transfers_out = []
        
        for batch_id, qty in batches_to_move:
            # 1. Deduct from Source
            src_row = self.inventory.add_stock(product_sku, source_wh, -qty, batch_number=batch_id)
            if not src_row or src_row.quantity < 0:
                raise ValueError(f"Insufficient stock in source batch {batch_id}")
            
            # 2. Add to Destination
            dst_row = self.inventory.add_stock(product_sku, dest_wh, qty, batch_number=batch_id)
            if not dst_row:
                 raise ValueError("Destination inventory row missing")

            # 3. Create Postgres Movements
            src_after = int(src_row.quantity)
            src_before = src_after + qty
            
            # Record 1: Source (Transfer Out)
            m_out = self.movements.create_movement(
                product_id=product.id,
                warehouse_id=src.id,
                movement_type="transfer_out",
                quantity=qty,
                unit_price=getattr(product, "unit_price", None),
                destination_warehouse_id=dst.id,
                destination_warehouse_name=dst.name,
                reference_number=reference_number,
                before_quantity=src_before,
                after_quantity=src_after,
                batch_number=batch_id,
            )
            transfers_out.append(m_out)

            dst_after = int(dst_row.quantity)
            dst_before = dst_after - qty

            # Record 2: Destination (Transfer In)
            m_in = self.movements.create_movement(
                product_id=product.id,
                warehouse_id=dst.id,
                movement_type="transfer_in",
                quantity=qty,
                unit_price=getattr(product, "unit_price", None),
                destination_warehouse_id=src.id,
                destination_warehouse_name=src.name,
                reference_number=reference_number,
                before_quantity=dst_before,
                after_quantity=dst_after,
                batch_number=batch_id,
            )

            # 4. Flush to generate IDs for logging
            self.db.flush()

            # 5. Log Events to MongoDB
            LogService.log_inventory_event(
                action_type="transfer_out",
                product_sku=product_sku,
                quantity_change=-qty,
                before_quantity=src_before,
                after_quantity=src_after,
                warehouse_name=source_wh,
                reference_id=str(m_out.id)
            )

            LogService.log_inventory_event(
                action_type="transfer_in",
                product_sku=product_sku,
                quantity_change=qty,
                before_quantity=dst_before,
                after_quantity=dst_after,
                warehouse_name=dest_wh,
                reference_id=str(m_in.id)
            )


        self.db.commit()
        if transfers_out:
            last_m = transfers_out[-1]
            self.db.refresh(last_m)
            return last_m
        return None