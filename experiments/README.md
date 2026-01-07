# SmartSupply Data Description

## Overview

This dataset contains simulated inventory management data for a consumer packaged goods (CPG) company, specifically modeled after PepsiCo's product portfolio. The data represents a smart supply chain system tracking products, warehouses, inventory levels, and product movements across four regional distribution centers.

**Generated on:** January 5, 2026  
**Version:** 1.0.0  
**Data Format:** JSON

## Data Structure

The dataset is organized into four main entities:

### 1. Products
- **Total Products:** 22
- **Categories:** Beverages, Snacks, Cereals
- **Price Range:** $0.99 - $5.49
- **Average Price:** $3.82

**Fields:**
- `id`: Unique product identifier (UUID)
- `sku`: Stock Keeping Unit code
- `name`: Product name
- `category`: Product category
- `unit_price`: Price per unit
- `unit`: Unit of measurement (e.g., "12-pack", "bag", "gallon")

### 2. Warehouses
- **Total Warehouses:** 4
- **Regions:** Southeast, Midwest, West, Northeast
- **Total Capacity:** 198,000 units

**Fields:**
- `id`: Unique warehouse identifier (UUID)
- `name`: Warehouse name
- `location`: City and state
- `region`: Geographic region
- `capacity`: Maximum storage capacity
- `latitude`: Geographic latitude
- `longitude`: Geographic longitude

**Warehouse Details:**
- Memphis Distribution Center (TN) - Southeast - 50,000 capacity
- Chicago Distribution Center (IL) - Midwest - 45,000 capacity
- Los Angeles Distribution Center (CA) - West - 55,000 capacity
- New Jersey Distribution Center (NJ) - Northeast - 48,000 capacity

### 3. Inventory
- **Total Records:** 88 (22 products × 4 warehouses)
- **Total Quantity:** 91,194 units
- **Average Quantity per Product per Warehouse:** 1,036.3 units
- **Low Stock Items:** 0 (all above reorder levels)

**Fields:**
- `id`: Unique inventory record identifier (UUID)
- `product_id`: Reference to product
- `product_sku`: Product SKU
- `product_name`: Product name
- `warehouse_id`: Reference to warehouse
- `warehouse_name`: Warehouse name
- `quantity`: Current stock level
- `reorder_level`: Minimum stock level before reorder
- `safety_stock`: Safety stock buffer
- `last_updated`: Timestamp of last inventory update

**Inventory Distribution by Warehouse:**
- Los Angeles Distribution Center: 23,602 units
- Memphis Distribution Center: 23,587 units
- Chicago Distribution Center: 22,433 units
- New Jersey Distribution Center: 21,572 units

### 4. Movements
- **Total Movements:** 320
- **Date Range:** December 6, 2025 - January 5, 2026
- **Total Value:** $225,710.18
- **Movement Types:** SALE, PURCHASE, DAMAGE, TRANSFER

**Fields:**
- `id`: Unique movement identifier (UUID)
- `product_id`: Reference to product
- `product_sku`: Product SKU
- `product_name`: Product name
- `warehouse_id`: Reference to warehouse
- `warehouse_name`: Warehouse name
- `movement_type`: Type of movement (SALE, PURCHASE, DAMAGE, TRANSFER)
- `quantity`: Quantity moved
- `unit_price`: Price per unit at time of movement
- `total_value`: Total monetary value
- `timestamp`: Date and time of movement
- `reference_number`: Transaction reference
- `destination_warehouse_id`: For transfers (optional)
- `destination_warehouse_name`: For transfers (optional)
- `damage_reason`: For damages (optional)

**Movement Summary:**
- **Sales:** 113 movements, $48,192.56 total value
- **Purchases:** 106 movements
- **Damages:** 53 movements, $5,269.76 total value
- **Transfers:** 48 movements, $53,365.26 total value

**Top Products by Sales Value:**
1. Fritos Original: $4,680.65
2. Life Cinnamon: $4,678.58
3. Sun Chips Garden Salsa: $4,456.83
4. Doritos Nacho Cheese: $4,435.86
5. Cap'n Crunch Berries: $3,851.16

## Recent Activity (Last 7 Days)
- **Recent Movements:** 84
- **Recent Sales Value:** $13,484.07

## Use Cases

This dataset is suitable for:

1. **Supply Chain Optimization:** Analyzing inventory levels and movement patterns
2. **Demand Forecasting:** Studying sales trends and seasonal patterns
3. **Warehouse Management:** Optimizing storage allocation and transfer logistics
4. **Financial Analysis:** Tracking inventory value and movement costs
5. **Data Science Projects:** Machine learning models for demand prediction, anomaly detection, etc.

## File Location

The data is stored in: `data/json/smartsupply_data.json`

## Data Quality Notes

- All inventory levels are above reorder points
- Geographic coordinates are provided for warehouse locations
- Timestamps are in ISO 8601 format
- Monetary values are in USD
- No missing values in core fields
- Referential integrity maintained between entities</content>
<parameter name="filePath">/Users/neehanth/Documents/Data Scientist/SmartSupply/smartsupply/README.md