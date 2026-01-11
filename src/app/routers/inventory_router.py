from fastapi import APIRouter, Depends, status, HTTPException, Query
from typing import Dict
from sqlalchemy.orm import Session

from app.schemas.schemas import InventoryAdjustmentRequest, InventoryTransferRequest
from app.services.inventory_service import InventoryService
from app.database.postgres import get_db

router = APIRouter(
    prefix="/inventory",
    tags=["Inventory"]
)

@router.get("/stock", response_model=int)
def get_stock(
    sku: str = Query(..., description="Product SKU"),
    warehouse_name: str = Query(..., description="Warehouse Name"),
    db: Session = Depends(get_db)
):
    """
    Get the current stock of a product in a specific warehouse.
    """
    service = InventoryService(db=db)
    try:
        return service.get_stock(product_sku=sku, warehouse_name=warehouse_name)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=str(e)
        )

@router.post("/adjustments", response_model=int)
def adjust_stock(
    request: InventoryAdjustmentRequest,
    db: Session = Depends(get_db)
):
    """
    Adjust inventory stock (inbound/outbound/damage/adjust).
    Returns the new quantity.
    """
    service = InventoryService(db=db)
    try:
        return service.move_stock(
            product_sku=request.product_sku,
            warehouse_name=request.warehouse_name,
            movement_type=request.movement_type,
            quantity=request.quantity
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=str(e)
        )

@router.post("/transfers", response_model=Dict[str, int])
def transfer_stock(
    request: InventoryTransferRequest,
    db: Session = Depends(get_db)
):
    """
    Transfer stock between two warehouses.
    Returns the new quantities for source and destination.
    """
    service = InventoryService(db=db)
    try:
        return service.transfer_stock(
            product_sku=request.product_sku,
            source_wh=request.source_warehouse,
            dest_wh=request.destination_warehouse,
            quantity=request.quantity
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )