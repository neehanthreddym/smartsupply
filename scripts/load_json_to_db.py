'''
Loads the json data to Postgres DB.

Workflow
1. Read the json file
2. Start a session
    * Load products
    * Load warehouses
    * Load inventory
    * Load movements
3. Commit the changes
4. Verify
    * Print the row count from each table
    Products -> 22
    Warehouses -> 4
    Inventory -> 88
    Movements -> 320
'''

import json
import os
from pathlib import Path
import traceback
from app.database.init_db import init_db
from app.database.postgres import SessionLocal
from app.models.inventory import Product, Warehouse, Inventory, Movement

# Read the json file
filepath = Path('data/json/smartsupply_data.json')

def load_data():
    if not os.path.exists(filepath):
        print(f"Error: Data file not found at {filepath}")
        return

    with open(filepath, 'r') as f:
        data = json.load(f)
    print("json file loaded successfully")

    db = SessionLocal()
    
    try:
        # Clear existing data (optional, but good for idempotency/testing)
        # db.query(Movement).delete()
        # db.query(Inventory).delete()
        # db.query(Product).delete()
        # db.query(Warehouse).delete()
        # db.commit()

        # 1. Load Products
        print("Loading Products...")
        products_data = data.get('products', [])
        for product in products_data:
            # Check if exists to avoid duplicates if re-running
            existing = db.query(Product).filter(Product.id == product['id']).first()
            if not existing:
                product = Product(**product)
                db.add(product)
        
        # 2. Load Warehouses
        print("Loading Warehouses...")
        warehouses_data = data.get('warehouses', [])
        for warehouse in warehouses_data:
            existing = db.query(Warehouse).filter(Warehouse.id == warehouse['id']).first()
            if not existing:
                warehouse = Warehouse(**warehouse)
                db.add(warehouse)

        # Commit to ensure foreign keys exist for inventory/movements
        db.commit()

        # 3. Load Inventory
        print("Loading Inventory...")
        inventory_data = data.get('inventory', [])
        for i in inventory_data:
            existing = db.query(Inventory).filter(Inventory.id == i['id']).first()
            if not existing:
                inventory_item = Inventory(**i)
                db.add(inventory_item)

        # 4. Load Movements
        print("Loading Movements...")
        movements_data = data.get('movements', [])
        for movement in movements_data:
            existing = db.query(Movement).filter(Movement.id == movement['id']).first()
            if not existing:
                movement = Movement(**movement)
                db.add(movement)

        db.commit()
        print("Data loaded to Postgres successfully!")

        # Verify
        p_count = db.query(Product).count()
        w_count = db.query(Warehouse).count()
        i_count = db.query(Inventory).count()
        m_count = db.query(Movement).count()

        print("\n--- Verification ---")
        print(f"Products: {p_count} (Expected: 22)")
        print(f"Warehouses: {w_count} (Expected: 4)")
        print(f"Inventory: {i_count} (Expected: 88)")
        print(f"Movements: {m_count} (Expected: 320)")

    except Exception as e:
        print(f"An error occurred: {e}")
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    # Ensure tables exist
    init_db()
    
    # Load the data to Postgres
    load_data()