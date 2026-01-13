from fastapi import APIRouter, Depends, status, HTTPException

from sqlalchemy.orm import Session

from app.schemas.schemas import InventoryAdjustmentRequest, InventoryTransferRequest, MovementResponse
from app.services.supply_service import InventoryService
from app.database.postgres import get_db

router = APIRouter(
    prefix="/movements",
    tags=["Movements"]
)

@router.post("/adjustments", response_model=MovementResponse)
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
            quantity=request.quantity,
            reference_number=request.reference_number,
            damage_reason=request.damage_reason,
            batch_number=request.batch_number
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=str(e)
        )

@router.post("/transfers", response_model=MovementResponse)
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
            quantity=request.quantity,
            reference_number=request.reference_number,
            batch_number=request.batch_number
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )