from app.models import inventory_models, user_models
from app.database.postgres import engine

print("Base object:", inventory_models.Base)
print("Registered tables:", inventory_models.Base.metadata.tables.keys())
'''
Output:
Base object: <class 'sqlalchemy.orm.decl_api.Base'>
Registered tables: dict_keys(['products', 'warehouses', 'inventory', 'inventory_movements'])
'''

# Create the database tables
def init_db():
    inventory_models.Base.metadata.create_all(bind=engine)