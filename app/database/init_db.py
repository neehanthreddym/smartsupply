from app.models import inventory
from app.database.postgres import engine

print("Base object:", inventory.Base)
print("Registered tables:", inventory.Base.metadata.tables.keys())
'''
Output:
Base object: <class 'sqlalchemy.orm.decl_api.Base'>
Registered tables: dict_keys(['products', 'warehouses', 'inventory', 'inventory_movements'])
'''

# Create the database tables
inventory.Base.metadata.create_all(bind=engine)