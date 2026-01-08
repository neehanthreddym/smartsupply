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

## Project Structure

The project follows a clean, modular architecture:

```
src/
└── app/
    ├── database/       # Database connection and initialization
    ├── models/         # SQLAlchemy ORM models
    ├── repositories/   # Data access layer (Repository Pattern)
    ├── schemas/        # Pydantic models (Data Validation)
    └── utils/          # Utility functions
```

### Key Components

*   **Repositories**: Utilized Repository pattern (e.g., `InventoryRepository`, `ProductRepository`, `WarehouseRepository`) to abstract database operations, ensuring clean separation between business logic and data access.