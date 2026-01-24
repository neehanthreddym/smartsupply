"""AI Agent Tools for SmartSupply Inventory Management."""

from app.tools.inventory_tools import (
    # Read-Only Tools
    query_inventory_stock,
    query_inventory_details,
    query_low_stock_items,
    query_movement_history,
    query_product_catalog,
    query_warehouse_catalog,
    # Soft Gate Tools
    create_product,
    create_warehouse,
    adjust_inventory_inbound,
    # Hard Gate Tools
    report_inventory_anomaly,
    adjust_inventory_outbound,
    transfer_inventory,
)

from app.tools.schemas import (
    ToolResponse,
    QueryStockInput,
    QueryDetailsInput,
    QueryLowStockInput,
    QueryMovementHistoryInput,
    QueryProductCatalogInput,
    QueryWarehouseCatalogInput,
    CreateProductInput,
    CreateWarehouseInput,
    AdjustInboundInput,
    ReportAnomalyInput,
    AdjustOutboundInput,
    TransferInventoryInput,
)

__all__ = [
    # Tools
    "query_inventory_stock",
    "query_inventory_details",
    "query_low_stock_items",
    "query_movement_history",
    "query_product_catalog",
    "query_warehouse_catalog",
    "create_product",
    "create_warehouse",
    "adjust_inventory_inbound",
    "report_inventory_anomaly",
    "adjust_inventory_outbound",
    "transfer_inventory",
    # Schemas
    "ToolResponse",
    "QueryStockInput",
    "QueryDetailsInput",
    "QueryLowStockInput",
    "QueryMovementHistoryInput",
    "QueryProductCatalogInput",
    "QueryWarehouseCatalogInput",
    "CreateProductInput",
    "CreateWarehouseInput",
    "AdjustInboundInput",
    "ReportAnomalyInput",
    "AdjustOutboundInput",
    "TransferInventoryInput",
]
