from fastapi import APIRouter, Depends, status, HTTPException, Request
from app.dependencies import get_current_active_user

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
    request: Request,
    body: InventoryAdjustmentRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Adjust inventory stock (inbound/outbound/damage/adjust).
    Returns the new quantity.
    """
    service = InventoryService(db=db, request_id=request.state.request_id)
    try:
        return service.move_stock(
            product_sku=body.product_sku,
            warehouse_name=body.warehouse_name,
            movement_type=body.movement_type,
            quantity=body.quantity,
            reference_number=body.reference_number,
            damage_reason=body.damage_reason,
            batch_number=body.batch_number
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=str(e)
        )

@router.post("/transfers", response_model=MovementResponse)
def transfer_stock(
    request: Request,
    body: InventoryTransferRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Transfer stock between two warehouses.
    Returns the new quantities for source and destination.
    """
    service = InventoryService(db=db, request_id=request.state.request_id)
    try:
        return service.transfer_stock(
            product_sku=body.product_sku,
            source_wh=body.source_warehouse,
            dest_wh=body.destination_warehouse,
            quantity=body.quantity,
            reference_number=body.reference_number,
            batch_number=body.batch_number
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )