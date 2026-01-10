from fastapi import APIRouter, Depends, status, HTTPException
from typing import List
from sqlalchemy.orm import Session

from app.schemas.schemas import ProductResponse, WarehouseResponse
from app.services.inventory_service import CatalogService
from app.database.postgres import get_db

router = APIRouter(
    prefix="/catalog",
    tags=["Catalog"]
)

@router.get("/products", response_model=List[ProductResponse])
def list_products(limit: int = None, db: Session = Depends(get_db)):
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
def get_product_by_sku(sku: str, db: Session = Depends(get_db)):
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

@router.get("/warehouses", response_model=List[WarehouseResponse])
def list_warehouses(limit: int = None, db: Session = Depends(get_db)):
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
def get_warehouse_by_id(warehouse_id: int, db: Session = Depends(get_db)):
    """
    Retireve a warehouse by its ID.

    Args:
        warehouse_id (int): The ID of the warehouse.
        db (Session): Database session dependency.
    
    Returns:
        WarehouseResponse: The warehouse details.
    """
    service = CatalogService(db=db)
    warehouse = service.get_warehouse_by_id(id=warehouse_id)
    if not warehouse:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Warehouse not found")
    return warehouse