from fastapi import APIRouter, Depends, status, HTTPException
from app.dependencies import get_current_active_user
from typing import List
from sqlalchemy.orm import Session

from app.schemas.schemas import (
    ProductResponse, WarehouseResponse, ProductCreateRequest, WarehouseCreateRequest
)
from app.services.supply_service import CatalogService
from app.database.postgres import get_db

router = APIRouter(
    prefix="/catalog",
    tags=["Catalog"]
)

@router.get("/products", response_model=List[ProductResponse])
def list_products(limit: int = None, db: Session = Depends(get_db), current_user = Depends(get_current_active_user)):
    """
    Retireve a list of products from the catalog.
    
    Args:
        limit (int, optional): Maximum number of products to return. If None, returns all products.
        db (Session): Database session dependency.

    Returns:
        List[ProductResponse]: A list of products.
    """
    service = CatalogService(db=db)
    products = service.list_products(limit=limit)
    return products

@router.get("/products/{sku}", response_model=ProductResponse)
def get_product_by_sku(sku: str, db: Session = Depends(get_db), current_user = Depends(get_current_active_user)):
    """
    Retrieve a product by its SKU code.

    Args:
        sku (str): The SKU code of the product.
        db (Session): Database session dependency.
    
    Returns:
        ProductResponse: The product details.
    """
    service = CatalogService(db=db)
    product = service.get_product_by_sku(sku=sku)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return product

@router.post("/products", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(product: ProductCreateRequest, db: Session = Depends(get_db), current_user = Depends(get_current_active_user)):
    """
    Create a new product in the catalog.
    """
    service = CatalogService(db=db)
    try:
        new_product = service.create_product(
            sku=product.sku,
            name=product.name,
            category=product.category,
            unit_price=product.unit_price,
            unit=product.unit
        )
        return new_product
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/warehouses", response_model=List[WarehouseResponse])
def list_warehouses(limit: int = None, db: Session = Depends(get_db), current_user = Depends(get_current_active_user)):
    """
    Return a list of warehouses.

    Args:
        limit (int, optional): Maximum number of warehouses to return. If None, returns all warehouses.
        db (Session): Database session dependency.
    """
    service = CatalogService(db=db)
    warehouses = service.list_warehouses(limit=limit)
    return warehouses

@router.get("/warehouses/{warehouse_id}", response_model=WarehouseResponse)
def get_warehouse_by_id(warehouse_id: str, db: Session = Depends(get_db), current_user = Depends(get_current_active_user)):
    """
    Retireve a warehouse by its ID.

    Args:
        warehouse_id (str): The ID of the warehouse.
        db (Session): Database session dependency.
    
    Returns:
        WarehouseResponse: The warehouse details.
    """
    service = CatalogService(db=db)
    warehouse = service.get_warehouse_by_id(warehouse_id=warehouse_id)
    if not warehouse:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Warehouse not found")
    return warehouse

@router.post("/warehouses", response_model=WarehouseResponse, status_code=status.HTTP_201_CREATED)
def create_warehouse(warehouse: WarehouseCreateRequest, db: Session = Depends(get_db), current_user = Depends(get_current_active_user)):
    """
    Create a new warehouse via API.
    """
    service = CatalogService(db=db)
    try:
        new_wh = service.create_warehouse(
            name=warehouse.name,
            location=warehouse.location,
            region=warehouse.region,
            capacity=warehouse.capacity,
            latitude=warehouse.latitude,
            longitude=warehouse.longitude
        )
        return new_wh
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))