from fastapi import APIRouter, Depends, status, HTTPException, Query
from typing import Dict, Optional, List
from sqlalchemy.orm import Session

from app.schemas.schemas import InventoryResponse
from app.services.supply_service import InventoryService
from app.database.postgres import get_db

router = APIRouter(
    prefix="/inventory",
    tags=["Inventory"]
)

@router.get("/stock", response_model=int)
def get_stock(
    sku: str = Query(..., description="Product SKU"),
    warehouse_name: Optional[str] = Query(None, description="Warehouse Name"),
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

@router.get("/details", response_model=List[InventoryResponse])
def get_inventory_details(
    sku: str = Query(..., description="Product SKU"),
    warehouse_name: Optional[str] = Query(None, description="Warehouse Name"),
    db: Session = Depends(get_db)
):
    """
    Get full inventory details + denormalized info.
    """
    service = InventoryService(db=db)
    try:
        result = service.get_inventory_record(product_sku=sku, warehouse_name=warehouse_name)
        if isinstance(result, list):
            return result
        return [result]
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=str(e)
        )