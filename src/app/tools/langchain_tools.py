"""
LangChain Tool Wrappers for Inventory Management.

This module wraps the 12 inventory tools with LangChain's @tool decorator,
making them discoverable and callable by AI agents.
"""

from typing import Optional, Dict, Any
from langchain.tools import tool
from sqlalchemy.orm import Session


def create_inventory_tools(db: Session, request_id: str = "langchain-agent"):
    """
    Create all 12 LangChain tools with database session injected.
    
    Args:
        db: SQLAlchemy database session
        request_id: Request ID for tracking (optional)
    
    Returns:
        List of LangChain tools ready for agent use
    """
    
    # Import the actual tool implementations
    from app.tools.inventory_tools import (
        query_inventory_stock as _query_stock,
        query_inventory_details as _query_details,
        query_low_stock_items as _query_low_stock,
        query_movement_history as _query_movements,
        query_product_catalog as _query_products,
        query_warehouse_catalog as _query_warehouses,
        create_product as _create_product,
        create_warehouse as _create_warehouse,
        adjust_inventory_inbound as _adjust_inbound,
        report_inventory_anomaly as _report_anomaly,
        adjust_inventory_outbound as _adjust_outbound,
        transfer_inventory as _transfer,
    )
    
    # =============================================================================
    # READ-ONLY TOOLS
    # =============================================================================
    
    @tool
    def query_inventory_stock(product_sku: str, warehouse_name: Optional[str] = None) -> dict:
        """
        Check current stock levels for a product.
        
        Use this to answer questions like:
        - "What's the stock for LAY-CH-ORIG?"
        - "How many units of Doritos do we have at Memphis?"
        
        Args:
            product_sku: Product SKU code (e.g., "LAY-CH-ORIG")
            warehouse_name: Optional warehouse name to filter by
        
        Returns:
            Dictionary with stock information and success status
        """
        result = _query_stock(db, request_id, product_sku, warehouse_name)
        return result.model_dump()
    
    @tool
    def query_inventory_details(product_sku: str, warehouse_name: Optional[str] = None) -> dict:
        """
        Get detailed inventory records including batch information.
        
        Use this for detailed inventory breakdowns with batch numbers,
        reorder levels, and safety stock information.
        
        Args:
            product_sku: Product SKU to query
            warehouse_name: Optional warehouse name filter
        
        Returns:
            Dictionary with detailed inventory records
        """
        result = _query_details(db, request_id, product_sku, warehouse_name)
        return result.model_dump()
    
    @tool
    def query_low_stock_items(limit: int = 100) -> dict:
        """
        Find products that are below reorder or safety stock levels.
        
        Use this to answer:
        - "What items need reordering?"
        - "Show me products running low"
        
        Args:
            limit: Maximum number of items to return (default: 100)
        
        Returns:
            Dictionary with list of low stock items
        """
        result = _query_low_stock(db, request_id, limit)
        return result.model_dump()
    
    @tool
    def query_movement_history(
        product_sku: Optional[str] = None,
        warehouse_name: Optional[str] = None,
        limit: int = 100
    ) -> dict:
        """
        View transaction history for products or warehouses.
        
        Provide at least one filter (product_sku OR warehouse_name).
        
        Use this to answer:
        - "Show me recent movements for LAY-CH-ORIG"
        - "What happened at Memphis warehouse yesterday?"
        
        Args:
            product_sku: Optional product SKU filter
            warehouse_name: Optional warehouse name filter
            limit: Maximum movements to return (default: 100)
        
        Returns:
            Dictionary with movement history
        """
        result = _query_movements(db, request_id, product_sku, warehouse_name, limit)
        return result.model_dump()
    
    @tool
    def query_product_catalog(sku: Optional[str] = None, limit: int = 100) -> dict:
        """
        Look up product information from the catalog.
        
        If sku is provided, returns that specific product.
        Otherwise returns a list of products.
        
        Use this to:
        - Find product details by SKU
        - Browse available products
        
        Args:
            sku: Optional specific SKU to look up
            limit: Maximum products to return if listing (default: 100)
        
        Returns:
            Dictionary with product information
        """
        result = _query_products(db, request_id, sku, limit)
        return result.model_dump()
    
    @tool
    def query_warehouse_catalog(warehouse_name: Optional[str] = None, limit: int = 100) -> dict:
        """
        Look up warehouse information from the catalog.
        
        If warehouse_name is provided, returns that specific warehouse.
        Otherwise returns a list of warehouses.
        
        Use this to:
        - Find warehouse details
        - Browse available warehouses
        - Get warehouse locations and capacity
        
        Args:
            warehouse_name: Optional specific warehouse to look up
            limit: Maximum warehouses to return if listing (default: 100)
        
        Returns:
            Dictionary with warehouse information
        """
        result = _query_warehouses(db, request_id, warehouse_name, limit)
        return result.model_dump()
    
    # =============================================================================
    # SOFT GATE TOOLS (Awareness Confirmation)
    # =============================================================================
    
    @tool
    def create_product(
        sku: str,
        name: str,
        category: str,
        unit_price: float,
        unit: str
    ) -> dict:
        """
        Add a new product to the catalog.
        
        ⚠️ SOFT GATE: Request user awareness confirmation before executing.
        
        Use when user wants to add a new product that doesn't exist yet.
        
        Args:
            sku: Unique product SKU code
            name: Product name
            category: Product category (e.g., "Snacks", "Beverages")
            unit_price: Price per unit in dollars
            unit: Unit of measure (e.g., "case", "unit", "kg")
        
        Returns:
            Dictionary with created product details
        """
        result = _create_product(db, request_id, sku, name, category, unit_price, unit)
        return result.model_dump()
    
    @tool
    def create_warehouse(
        name: str,
        location: str,
        region: str,
        capacity: int,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None
    ) -> dict:
        """
        Add a new warehouse location.
        
        ⚠️ SOFT GATE: Request user awareness confirmation before executing.
        
        Use when adding a new distribution center or storage facility.
        
        Args:
            name: Warehouse name
            location: Physical address/location
            region: Geographic region
            capacity: Storage capacity in units
            latitude: Optional GPS latitude
            longitude: Optional GPS longitude
        
        Returns:
            Dictionary with created warehouse details
        """
        result = _create_warehouse(
            db, request_id, name, location, region, capacity, latitude, longitude
        )
        return result.model_dump()
    
    @tool
    def adjust_inventory_inbound(
        product_sku: str,
        warehouse_name: str,
        quantity: int,
        reference_number: Optional[str] = None,
        batch_number: Optional[str] = None
    ) -> dict:
        """
        Receive stock into inventory (increases quantity).
        
        ⚠️ SOFT GATE: Request user awareness confirmation before executing.
        
        Use for:
        - Receiving new shipments
        - Purchase orders arriving
        - Stock replenishment
        
        Args:
            product_sku: Product SKU to receive
            warehouse_name: Destination warehouse
            quantity: Quantity to receive (must be positive)
            reference_number: Optional PO number or reference
            batch_number: Optional batch/lot number for tracking
        
        Returns:
            Dictionary with movement record
        """
        result = _adjust_inbound(
            db, request_id, product_sku, warehouse_name, quantity, reference_number, batch_number
        )
        return result.model_dump()
    
    # =============================================================================
    # HARD GATE TOOLS (Strict Confirmation Required)
    # =============================================================================
    
    @tool
    def report_inventory_anomaly(
        product_sku: str,
        warehouse_name: str,
        quantity: int,
        reason: str,
        reference_number: Optional[str] = None
    ) -> dict:
        """
        Log inventory anomaly like damage, theft, or expiration.
        
        🚨 HARD GATE: Requires strict user confirmation before executing.
        This DECREASES inventory and creates an audit trail.
        
        Use for:
        - Damaged goods
        - Theft or loss
        - Expired products
        - Quality control failures
        
        Args:
            product_sku: Affected product SKU
            warehouse_name: Location where anomaly occurred
            quantity: Quantity affected (must be positive)
            reason: Detailed explanation (required for audit)
            reference_number: Optional incident reference number
        
        Returns:
            Dictionary with anomaly record
        """
        result = _report_anomaly(
            db, request_id, product_sku, warehouse_name, quantity, reason, reference_number
        )
        return result.model_dump()
    
    @tool
    def adjust_inventory_outbound(
        product_sku: str,
        warehouse_name: str,
        quantity: int,
        reference_number: Optional[str] = None,
        batch_number: Optional[str] = None
    ) -> dict:
        """
        Ship stock from inventory (decreases quantity).
        
        🚨 HARD GATE: Requires strict user confirmation before executing.
        Uses FIFO (First-In-First-Out) if batch not specified.
        
        Use for:
        - Customer orders/shipments
        - Sales orders
        - Distribution to stores
        
        Args:
            product_sku: Product SKU to ship
            warehouse_name: Source warehouse
            quantity: Quantity to ship (must be positive)
            reference_number: Optional sales order or shipment reference
            batch_number: Optional specific batch (FIFO if not specified)
        
        Returns:
            Dictionary with movement record
        """
        result = _adjust_outbound(
            db, request_id, product_sku, warehouse_name, quantity, reference_number, batch_number
        )
        return result.model_dump()
    
    @tool
    def transfer_inventory(
        product_sku: str,
        source_warehouse: str,
        destination_warehouse: str,
        quantity: int,
        reference_number: Optional[str] = None,
        batch_number: Optional[str] = None
    ) -> dict:
        """
        Move stock between warehouses.
        
        🚨 HARD GATE: Requires strict user confirmation before executing.
        Uses FIFO (First-In-First-Out) if batch not specified.
        
        Use for:
        - Inter-warehouse transfers
        - Rebalancing inventory
        - Moving stock closer to demand
        
        Args:
            product_sku: Product SKU to transfer
            source_warehouse: Origin warehouse name
            destination_warehouse: Destination warehouse name
            quantity: Quantity to transfer (must be positive)
            reference_number: Optional transfer order reference
            batch_number: Optional specific batch (FIFO if not specified)
        
        Returns:
            Dictionary with transfer movement record
        """
        result = _transfer(
            db, request_id, product_sku, source_warehouse, 
            destination_warehouse, quantity, reference_number, batch_number
        )
        return result.model_dump()
    
    # Return all tools as a list
    return [
        # Read-only (6)
        query_inventory_stock,
        query_inventory_details,
        query_low_stock_items,
        query_movement_history,
        query_product_catalog,
        query_warehouse_catalog,
        # Soft gate (3)
        create_product,
        create_warehouse,
        adjust_inventory_inbound,
        # Hard gate (3)
        report_inventory_anomaly,
        adjust_inventory_outbound,
        transfer_inventory,
    ]
