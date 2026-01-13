from fastapi import FastAPI
import uvicorn
from app.routers import catalog_router, inventory_router, movement_router

app = FastAPI(
    title="SmartSupply API",
    description="Inventory Management System",
    version="1.0.0"
)

app.include_router(catalog_router.router)
app.include_router(inventory_router.router)
app.include_router(movement_router.router)

@app.get("/")
def root():
    return {"message": "Welcome to SmartSupply API"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)