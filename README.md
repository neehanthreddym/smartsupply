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
- **Secure Access**: User Authentication via OAuth2 (JWT) with password hashing.
- **Batch-Level Inventory**: Tracks stock by batch number to ensure traceability and expiry management.
- **FIFO Logic**: Automatically enforces First-In-First-Out for stock deduction when no batch is specified.
- **Catalog Management**: Full API support (`POST/GET`) for creating and managing Products and Warehouses.
- **Movement Tracking**: Detailed logs of every inventory change (Inbound, Outbound, Transfer, Adjustments).
- **Event Logging (MongoDB)**: Immutable audit logs for all state-changing operations and conversation history.

## Hybrid Database Architecture

SmartSupply uses **PostgreSQL** as the "Source of Truth" for current state (Inventory, Users) and **MongoDB** as the "System of Record" for history (Audit Logs).

### MongoDB Collections
1.  **`conversation_logs`**: Traces User <-> Agent interactions (Intent, Tool Selection, Result).
2.  **`audit_logs`**: Immutable record of all inventory and catalog changes.
    *   **Traceability**: Every batch movement is logged strictly with `before` and `after` quantities.
    *   **Scope**: Covers `create_product`, `create_warehouse`, `inbound`, `outbound`, `transfer`, and `damage` events.

## Project Structure

The project follows a clean, modular architecture:

```
src/
└── app/
    ├── core/           # Security & Config (JWT, Hashing)
    ├── database/       # Database connection
    ├── models/         # SQLAlchemy ORM models (User, Inventory, etc.)
    ├── routers/        # API Endpoints (Auth, User, Catalog, Inventory, Movement)
    ├── repositories/   # Data access layer
    ├── schemas/        # Pydantic validation models
    ├── services/       # Business logic (SupplyService)
    └── utils/          # Utilities
```

### Key Components

*   **Security Layer**:
    *   `auth_router`: Handles Login (`/login`) and Registration (`/register`).
    *   `security.py`: Manages JWT creation and `bcrypt` password hashing.
    *   `dependencies.py`: Provides `get_current_active_user` to specific protect routes.
*   **Service Layer**: The core business logic residing in `supply_service.py`.
    *   `InventoryService`: Handles stock movements, FIFO logic, and batch validation.
    *   `CatalogService`: Manages product creation and warehouse lookups.
    *   `LogService`: Write-only service that safely pushes immutable events to MongoDB.
*   **Routers**:
    *   `catalog_router`: Manage Products and Warehouses (Protected).
    *   `inventory_router`: Query stock levels (Protected).
    *   `movement_router`: Execute transfers and adjustments (Protected).

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

### Authentication Usage
1.  **Register**: POST to `/register` with email and password.
2.  **Login**: POST to `/login` (form-data) to get a Bearer Token.
3.  **Access API**: Include the token in the `Authorization` header (`Bearer <token>`) for all Inventory/Catalog requests.