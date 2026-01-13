# SmartSupply: Hybrid-DB Supply Chain AI Agent API

## Project Overview
SmartSupply is a robust FastAPI microservice designed to transform how supply chain managers interact with data. By integrating **PostgreSQL** for transactional inventory management and **MongoDB** for flexible audit logging, it provides a reliable and scalable foundation. The core of SmartSupply is an **Autonomous AI Agent** (built with LangChain/LangGraph) that empowers users to query stock levels and report anomalies using natural language.

## Database Schema (PostgreSQL)

> ⚠️ **Note:** The data shown in this diagram is **synthetic (fake)** and was **generated using a Python script** for development and demonstration purposes only.

<img src="smartsupply_data.png" alt="ER diagram" width="700"/>

## Dataset Statistics
The PostgreSQL database is seeded with the following synthetic data:
*   **Products**: 22
*   **Warehouses**: 4
*   **Inventory Records**: 88
*   **Movement History**: 320 records

## Key Features
- **Batch-Level Inventory**: Tracks stock by batch number to ensure traceability and expiry management.
- **FIFO Logic**: Automatically enforces First-In-First-Out for stock deduction when no batch is specified.
- **Catalog Management**: Full API support (`POST/GET`) for creating and managing Products and Warehouses.
- **Movement Tracking**: Detailed logs of every inventory change (Inbound, Outbound, Transfer, Adjustments).

## Project Structure

The project follows a clean, modular architecture:

```
src/
└── app/
    ├── database/       # Database connection
    ├── models/         # SQLAlchemy ORM models
    ├── routers/        # API Endpoints (Catalog, Inventory, Movement)
    ├── repositories/   # Data access layer
    ├── schemas/        # Pydantic validation models
    ├── services/       # Business logic (SupplyService)
    └── utils/          # Utilities
```

### Key Components

*   **Service Layer**: The core business logic residing in `supply_service.py`.
    *   `InventoryService`: Handles stock movements, FIFO logic, and batch validation.
    *   `CatalogService`: Manages product creation and warehouse lookups.
*   **Routers**:
    *   `catalog_router`: Manage Products and Warehouses.
    *   `inventory_router`: Query stock levels.
    *   `movement_router`: Execute transfers and adjustments.

## How to Run

1.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
2.  **Start the Server**:
    ```bash
    uvicorn main:app --reload
    ```
    The API will be available at `http://localhost:8000`. API Docs at `http://localhost:8000/docs`.