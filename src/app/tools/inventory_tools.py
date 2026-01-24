"""
AI Agent Tools for Inventory Management.

This module provides 12 callable tools organized by gate type:
- Read-Only (6): No confirmation needed
- Soft Gate (3): Awareness confirmation
- Hard Gate (3): Strict confirmation required

Each tool wraps service layer methods and returns a consistent ToolResponse.
"""

from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
from app.services.supply_service import CatalogService, InventoryService
from app.tools.schemas import ToolResponse


def _serialize_model(obj) -> Dict[str, Any]:
    """Convert SQLAlchemy model to dict, handling datetime."""
    if obj is None:
        return None
    if hasattr(obj, "__dict__"):
        result = {}
        for key, value in obj.__dict__.items():
            if key.startswith("_"):
                continue
            if hasattr(value, "isoformat"):
                result[key] = value.isoformat()
            else:
                result[key] = value
        return result
    return obj


def _serialize_list(items: List) -> List[Dict[str, Any]]:
    """Convert list of SQLAlchemy models to list of dicts."""
    return [_serialize_model(item) for item in items]


# =============================================================================
# READ-ONLY TOOLS (No Gate Required)
# =============================================================================

def query_inventory_stock(
    db: Session,
    request_id: str,
    product_sku: str,
    warehouse_name: Optional[str] = None
) -> ToolResponse:
    """
    Check stock levels for a product, optionally filtered by warehouse.
    
    Returns a single quantity value:
    - If warehouse_name is provided: stock at that specific warehouse
    - If warehouse_name is NOT provided: total stock across ALL warehouses (aggregate sum)
    
    Note: This tool returns only a total quantity. To see stock levels broken down
    by warehouse, use query_inventory_details instead.
    
    Args:
        db: Database session
        request_id: Request tracking ID
        product_sku: Product SKU to check
        warehouse_name: Optional warehouse filter
    
    Returns:
        ToolResponse with stock quantity (single number)
    """
    try:
        service = InventoryService(db=db, request_id=request_id)
        stock = service.get_stock(product_sku=product_sku, warehouse_name=warehouse_name)
        
        location_msg = f" at {warehouse_name}" if warehouse_name else " (all warehouses)"
        return ToolResponse(
            success=True,
            data={"product_sku": product_sku, "quantity": stock, "warehouse": warehouse_name},
            message=f"Stock for {product_sku}{location_msg}: {stock} units",
            gate_type="read_only"
        )
    except ValueError as e:
        return ToolResponse(
            success=False,
            data=None,
            message=str(e),
            gate_type="read_only"
        )


def query_inventory_details(
    db: Session,
    request_id: str,
    product_sku: str,
    warehouse_name: Optional[str] = None
) -> ToolResponse:
    """
    Get full inventory records with batch info for a product.
    
    Returns detailed inventory records including warehouse information:
    - If warehouse_name is provided: all batches at that specific warehouse
    - If warehouse_name is NOT provided: all inventory records across ALL warehouses
      (showing which warehouse each batch is located at)
    
    Use this tool when you need to see stock levels broken down by warehouse,
    batch numbers, or other detailed inventory information.
    
    Args:
        db: Database session
        request_id: Request tracking ID
        product_sku: Product SKU to query
        warehouse_name: Optional warehouse filter
    
    Returns:
        ToolResponse with detailed inventory records (list of records with warehouse info)
    """
    try:
        service = InventoryService(db=db, request_id=request_id)
        records = service.get_inventory_record(product_sku=product_sku, warehouse_name=warehouse_name)
        
        if isinstance(records, list):
            data = _serialize_list(records)
        else:
            data = [_serialize_model(records)]
        
        return ToolResponse(
            success=True,
            data=data,
            message=f"Found {len(data)} inventory record(s) for {product_sku}",
            gate_type="read_only"
        )
    except ValueError as e:
        return ToolResponse(
            success=False,
            data=None,
            message=str(e),
            gate_type="read_only"
        )


def query_low_stock_items(
    db: Session,
    request_id: str,
    limit: int = 100
) -> ToolResponse:
    """
    Find products that are below reorder or safety stock levels.
    
    Use this tool to identify products that need restocking. Returns inventory
    records where current quantity is at or below the reorder_level or safety_stock
    threshold. Results include warehouse locations and current quantities.
    
    Common use cases:
    - "What products need reordering?"
    - "Show me low stock items"
    - "Which items are running low?"
    
    Args:
        db: Database session
        request_id: Request tracking ID
        limit: Maximum items to return (default: 100)
    
    Returns:
        ToolResponse with list of low stock inventory records (includes SKU, warehouse, quantity)
    """
    try:
        service = InventoryService(db=db, request_id=request_id)
        items = service.get_low_stock(limit=limit)
        data = _serialize_list(items)
        
        return ToolResponse(
            success=True,
            data=data,
            message=f"Found {len(data)} item(s) below reorder/safety stock levels",
            gate_type="read_only"
        )
    except Exception as e:
        return ToolResponse(
            success=False,
            data=None,
            message=f"Error querying low stock: {str(e)}",
            gate_type="read_only"
        )


def query_movement_history(
    db: Session,
    request_id: str,
    product_sku: Optional[str] = None,
    warehouse_name: Optional[str] = None,
    limit: int = 100
) -> ToolResponse:
    """
    View transaction/movement history filtered by product or warehouse.
    
    Returns a chronological list of all inventory movements (inbound, outbound,
    transfers, damages, etc.) for auditing and tracking purposes. Each record includes
    movement type, quantity, timestamps, and reference numbers.
    
    At least one filter (product_sku OR warehouse_name) must be provided.
    
    Common use cases:
    - "Show me all movements for product X"
    - "What happened at warehouse Y recently?"
    - "Track movement history for SKU123"
    
    Args:
        db: Database session
        request_id: Request tracking ID
        product_sku: Optional product SKU filter (returns movements for this product)
        warehouse_name: Optional warehouse filter (returns movements at this warehouse)
        limit: Maximum movements to return (default: 100, most recent first)
    
    Returns:
        ToolResponse with movement history list (chronological, includes type, quantity, timestamps)
    """
    if not product_sku and not warehouse_name:
        return ToolResponse(
            success=False,
            data=None,
            message="Please provide either product_sku or warehouse_name to filter movements",
            gate_type="read_only"
        )
    
    try:
        service = InventoryService(db=db, request_id=request_id)
        
        if product_sku:
            movements = service.get_movements_by_sku(product_sku=product_sku, limit=limit)
            filter_desc = f"product {product_sku}"
        else:
            movements = service.get_movements_by_warehouse(warehouse_name=warehouse_name, limit=limit)
            filter_desc = f"warehouse {warehouse_name}"
        
        data = _serialize_list(movements)
        
        return ToolResponse(
            success=True,
            data=data,
            message=f"Found {len(data)} movement(s) for {filter_desc}",
            gate_type="read_only"
        )
    except ValueError as e:
        return ToolResponse(
            success=False,
            data=None,
            message=str(e),
            gate_type="read_only"
        )


def query_product_catalog(
    db: Session,
    request_id: str,
    sku: Optional[str] = None,
    limit: int = 100
) -> ToolResponse:
    """
    Look up product information from the catalog.
    
    Returns product master data including SKU, name, category, unit price, and unit
    of measure. Use this to verify product details, check if a product exists, or
    browse the product catalog.
    
    Behavior:
    - If SKU is provided: returns that specific product (or error if not found)
    - If SKU is NOT provided: returns a list of all products (up to limit)
    
    Common use cases:
    - "Does product X exist in the catalog?"
    - "What's the price of SKU123?"
    - "List all available products"
    - "Show me products in the catalog"
    
    Args:
        db: Database session
        request_id: Request tracking ID
        sku: Optional specific SKU to look up
        limit: Maximum products to return if listing (default: 100)
    
    Returns:
        ToolResponse with product data (single product or list)
    """
    try:
        service = CatalogService(db=db, request_id=request_id)
        
        if sku:
            product = service.get_product_by_sku(sku=sku)
            if not product:
                return ToolResponse(
                    success=False,
                    data=None,
                    message=f"Product with SKU '{sku}' not found",
                    gate_type="read_only"
                )
            data = _serialize_model(product)
            return ToolResponse(
                success=True,
                data=data,
                message=f"Found product: {product.name} ({sku})",
                gate_type="read_only"
            )
        else:
            products = service.list_products(limit=limit)
            data = _serialize_list(products)
            return ToolResponse(
                success=True,
                data=data,
                message=f"Found {len(data)} product(s) in catalog",
                gate_type="read_only"
            )
    except Exception as e:
        return ToolResponse(
            success=False,
            data=None,
            message=f"Error querying products: {str(e)}",
            gate_type="read_only"
        )


def query_warehouse_catalog(
    db: Session,
    request_id: str,
    warehouse_name: Optional[str] = None,
    limit: int = 100
) -> ToolResponse:
    """
    Look up warehouse information from the catalog.
    
    Returns warehouse master data including name, location, region, capacity, and
    geographic coordinates. Use this to verify warehouse details, check if a
    warehouse exists, or browse all warehouse locations.
    
    Behavior:
    - If warehouse_name is provided: returns that specific warehouse (or error if not found)
    - If warehouse_name is NOT provided: returns a list of all warehouses (up to limit)
    
    Common use cases:
    - "Does warehouse X exist?"
    - "Where is the Atlanta warehouse located?"
    - "List all warehouse locations"
    - "Show me all distribution centers"
    
    Args:
        db: Database session
        request_id: Request tracking ID
        warehouse_name: Optional specific warehouse to look up
        limit: Maximum warehouses to return if listing (default: 100)
    
    Returns:
        ToolResponse with warehouse data (single warehouse or list)
    """
    try:
        service = CatalogService(db=db, request_id=request_id)
        
        if warehouse_name:
            # Use warehouse repository directly since service has get_by_id
            warehouse = service.warehouses.get_by_name(warehouse_name)
            if not warehouse:
                return ToolResponse(
                    success=False,
                    data=None,
                    message=f"Warehouse '{warehouse_name}' not found",
                    gate_type="read_only"
                )
            data = _serialize_model(warehouse)
            return ToolResponse(
                success=True,
                data=data,
                message=f"Found warehouse: {warehouse.name} in {warehouse.region}",
                gate_type="read_only"
            )
        else:
            warehouses = service.list_warehouses(limit=limit)
            data = _serialize_list(warehouses)
            return ToolResponse(
                success=True,
                data=data,
                message=f"Found {len(data)} warehouse(s) in catalog",
                gate_type="read_only"
            )
    except Exception as e:
        return ToolResponse(
            success=False,
            data=None,
            message=f"Error querying warehouses: {str(e)}",
            gate_type="read_only"
        )


# =============================================================================
# SOFT GATE TOOLS (Awareness Confirmation Required)
# =============================================================================

def create_product(
    db: Session,
    request_id: str,
    sku: str,
    name: str,
    category: str,
    unit_price: float,
    unit: str
) -> ToolResponse:
    """
    Add a new product to the catalog.
    
    Creates a new product master record with SKU, name, category, pricing, and unit
    information. The SKU must be unique - attempting to create a product with an
    existing SKU will fail.
    
    GATE TYPE: SOFT GATE - Requires user awareness confirmation before execution.
    
    Use this when:
    - A new product needs to be added to the catalog
    - Before receiving inbound stock for a new product (SKU must exist in catalog first)
    
    Args:
        db: Database session
        request_id: Request tracking ID
        sku: Unique product SKU (must not already exist)
        name: Product name
        category: Product category (e.g., 'Beverages', 'Snacks')
        unit_price: Price per unit (decimal)
        unit: Unit of measure (e.g., 'bottle', 'case', 'kg')
    
    Returns:
        ToolResponse with created product data
    """
    try:
        service = CatalogService(db=db, request_id=request_id)
        product = service.create_product(
            sku=sku,
            name=name,
            category=category,
            unit_price=unit_price,
            unit=unit
        )
        db.commit()
        
        return ToolResponse(
            success=True,
            data=_serialize_model(product),
            message=f"Created new product: {name} (SKU: {sku})",
            gate_type="soft_gate"
        )
    except ValueError as e:
        return ToolResponse(
            success=False,
            data=None,
            message=str(e),
            gate_type="soft_gate"
        )


def create_warehouse(
    db: Session,
    request_id: str,
    name: str,
    location: str,
    region: str,
    capacity: int,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None
) -> ToolResponse:
    """
    Add a new warehouse location.
    
    Creates a new warehouse master record with name, location, region, capacity, and
    optional geographic coordinates. The warehouse name must be unique - attempting
    to create a warehouse with an existing name will fail.
    
    GATE TYPE: SOFT GATE - Requires user awareness confirmation before execution.
    
    Use this when:
    - A new distribution center or warehouse location needs to be registered
    - Before receiving inventory at a new location (warehouse must exist in catalog first)
    
    Args:
        db: Database session
        request_id: Request tracking ID
        name: Warehouse name (must be unique)
        location: Physical address
        region: Geographic region (e.g., 'Northeast', 'West Coast')
        capacity: Storage capacity (integer)
        latitude: Optional latitude coordinate for mapping
        longitude: Optional longitude coordinate for mapping
    
    Returns:
        ToolResponse with created warehouse data
    """
    try:
        service = CatalogService(db=db, request_id=request_id)
        warehouse = service.create_warehouse(
            name=name,
            location=location,
            region=region,
            capacity=capacity,
            latitude=latitude,
            longitude=longitude
        )
        db.commit()
        
        return ToolResponse(
            success=True,
            data=_serialize_model(warehouse),
            message=f"Created new warehouse: {name} in {region}",
            gate_type="soft_gate"
        )
    except ValueError as e:
        return ToolResponse(
            success=False,
            data=None,
            message=str(e),
            gate_type="soft_gate"
        )


def adjust_inventory_inbound(
    db: Session,
    request_id: str,
    product_sku: str,
    warehouse_name: str,
    quantity: int,
    reference_number: Optional[str] = None,
    batch_number: Optional[str] = None
) -> ToolResponse:
    """
    Receive stock into inventory (increases quantity).
    
    Records incoming inventory at a warehouse, increasing stock levels. Creates a
    movement record for audit trails. Both the product SKU and warehouse must already
    exist in the catalog.
    
    GATE TYPE: SOFT GATE - Requires user awareness confirmation before execution.
    
    Use this when:
    - Receiving shipments from suppliers
    - Recording purchase orders being delivered
    - Adding stock after production
    
    Args:
        db: Database session
        request_id: Request tracking ID
        product_sku: Product to receive (must exist in catalog)
        warehouse_name: Destination warehouse (must exist in catalog)
        quantity: Quantity to receive (must be positive integer)
        reference_number: Optional PO number or shipment reference
        batch_number: Optional batch/lot number for tracking
    
    Returns:
        ToolResponse with movement record (includes before/after quantities)
    """
    if quantity <= 0:
        return ToolResponse(
            success=False,
            data=None,
            message="Quantity must be a positive number",
            gate_type="soft_gate"
        )
    
    try:
        service = InventoryService(db=db, request_id=request_id)
        movement = service.move_stock(
            product_sku=product_sku,
            warehouse_name=warehouse_name,
            movement_type="inbound",
            quantity=quantity,
            reference_number=reference_number,
            batch_number=batch_number
        )
        
        return ToolResponse(
            success=True,
            data=_serialize_model(movement),
            message=f"Received {quantity} units of {product_sku} at {warehouse_name}",
            gate_type="soft_gate"
        )
    except ValueError as e:
        return ToolResponse(
            success=False,
            data=None,
            message=str(e),
            gate_type="soft_gate"
        )


# =============================================================================
# HARD GATE TOOLS (Strict Confirmation Required)
# =============================================================================

def report_inventory_anomaly(
    db: Session,
    request_id: str,
    product_sku: str,
    warehouse_name: str,
    quantity: int,
    reason: str,
    reference_number: Optional[str] = None
) -> ToolResponse:
    """
    Log inventory anomaly (damage, theft, expiration, etc.).
    
    Records inventory shrinkage due to damage, loss, theft, expiration, or other
    anomalies. Decreases stock levels and creates a permanent audit trail with the
    reason for the loss. A reason is REQUIRED (minimum 3 characters).
    
    GATE TYPE: HARD GATE - Requires strict confirmation before execution.
    This reduces inventory and creates an audit trail.
    
    Use this when:
    - Products are damaged and cannot be sold
    - Inventory is lost or stolen
    - Products have expired and must be discarded
    - Recording any inventory shrinkage that needs documentation
    
    Args:
        db: Database session
        request_id: Request tracking ID
        product_sku: Affected product (must exist in catalog)
        warehouse_name: Location of anomaly (must exist in catalog)
        quantity: Quantity affected (must be positive, cannot exceed available stock)
        reason: Explanation (required, min 3 chars, e.g., 'damaged during handling', 'expired')
        reference_number: Optional incident/claim reference number
    
    Returns:
        ToolResponse with anomaly movement record (includes reason in audit trail)
    """
    if quantity <= 0:
        return ToolResponse(
            success=False,
            data=None,
            message="Quantity must be a positive number",
            gate_type="hard_gate"
        )
    
    if not reason or len(reason.strip()) < 3:
        return ToolResponse(
            success=False,
            data=None,
            message="A valid reason is required for anomaly reporting",
            gate_type="hard_gate"
        )
    
    try:
        service = InventoryService(db=db, request_id=request_id)
        movement = service.move_stock(
            product_sku=product_sku,
            warehouse_name=warehouse_name,
            movement_type="damage",
            quantity=quantity,
            reference_number=reference_number,
            damage_reason=reason.strip()
        )
        
        return ToolResponse(
            success=True,
            data=_serialize_model(movement),
            message=f"Reported anomaly: {quantity} units of {product_sku} at {warehouse_name} ({reason})",
            gate_type="hard_gate"
        )
    except ValueError as e:
        return ToolResponse(
            success=False,
            data=None,
            message=str(e),
            gate_type="hard_gate"
        )


def adjust_inventory_outbound(
    db: Session,
    request_id: str,
    product_sku: str,
    warehouse_name: str,
    quantity: int,
    reference_number: Optional[str] = None,
    batch_number: Optional[str] = None
) -> ToolResponse:
    """
    Ship stock from inventory (decreases quantity).
    
    Records outbound shipments from a warehouse, decreasing stock levels. Uses FIFO
    (First In, First Out) logic to select batches automatically, or you can specify
    a specific batch. Stock must be available before shipping.
    
    GATE TYPE: HARD GATE - Requires strict confirmation before execution.
    Uses FIFO deduction if batch_number is not specified.
    
    Use this when:
    - Fulfilling customer orders
    - Shipping to retailers or distributors
    - Recording any outbound stock movement
    
    Args:
        db: Database session
        request_id: Request tracking ID
        product_sku: Product to ship (must exist in catalog)
        warehouse_name: Source warehouse (must exist in catalog and have sufficient stock)
        quantity: Quantity to ship (must be positive, cannot exceed available stock)
        reference_number: Optional sales order or shipment reference
        batch_number: Optional specific batch to ship from (uses FIFO if not specified)
    
    Returns:
        ToolResponse with movement record (includes before/after quantities, batch info)
    """
    if quantity <= 0:
        return ToolResponse(
            success=False,
            data=None,
            message="Quantity must be a positive number",
            gate_type="hard_gate"
        )
    
    try:
        service = InventoryService(db=db, request_id=request_id)
        movement = service.move_stock(
            product_sku=product_sku,
            warehouse_name=warehouse_name,
            movement_type="outbound",
            quantity=quantity,
            reference_number=reference_number,
            batch_number=batch_number
        )
        
        return ToolResponse(
            success=True,
            data=_serialize_model(movement),
            message=f"Shipped {quantity} units of {product_sku} from {warehouse_name}",
            gate_type="hard_gate"
        )
    except ValueError as e:
        return ToolResponse(
            success=False,
            data=None,
            message=str(e),
            gate_type="hard_gate"
        )


def transfer_inventory(
    db: Session,
    request_id: str,
    product_sku: str,
    source_warehouse: str,
    destination_warehouse: str,
    quantity: int,
    reference_number: Optional[str] = None,
    batch_number: Optional[str] = None
) -> ToolResponse:
    """
    Move stock between warehouses.
    
    Transfers inventory from one warehouse location to another, decreasing stock at
    the source and increasing it at the destination. Creates movement records at both
    locations for full audit trail. Uses FIFO logic if batch is not specified.
    
    GATE TYPE: HARD GATE - Requires strict confirmation before execution.
    Uses FIFO selection if batch_number is not specified.
    
    Use this when:
    - Rebalancing inventory across locations
    - Moving stock closer to demand
    - Consolidating inventory
    
    Args:
        db: Database session
        request_id: Request tracking ID
        product_sku: Product to transfer (must exist in catalog)
        source_warehouse: Origin location (must exist and have sufficient stock)
        destination_warehouse: Destination location (must exist, cannot be same as source)
        quantity: Quantity to transfer (must be positive, cannot exceed source stock)
        reference_number: Optional transfer order or authorization reference
        batch_number: Optional specific batch to transfer (uses FIFO if not specified)
    
    Returns:
        ToolResponse with transfer movement record (includes both source and destination info)
    """
    if quantity <= 0:
        return ToolResponse(
            success=False,
            data=None,
            message="Quantity must be a positive number",
            gate_type="hard_gate"
        )
    
    if source_warehouse == destination_warehouse:
        return ToolResponse(
            success=False,
            data=None,
            message="Source and destination warehouses cannot be the same",
            gate_type="hard_gate"
        )
    
    try:
        service = InventoryService(db=db, request_id=request_id)
        movement = service.transfer_stock(
            product_sku=product_sku,
            source_wh=source_warehouse,
            dest_wh=destination_warehouse,
            quantity=quantity,
            reference_number=reference_number,
            batch_number=batch_number
        )
        
        return ToolResponse(
            success=True,
            data=_serialize_model(movement),
            message=f"Transferred {quantity} units of {product_sku} from {source_warehouse} to {destination_warehouse}",
            gate_type="hard_gate"
        )
    except ValueError as e:
        return ToolResponse(
            success=False,
            data=None,
            message=str(e),
            gate_type="hard_gate"
        )
