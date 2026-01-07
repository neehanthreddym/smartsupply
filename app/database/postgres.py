"""SQLAlchemy engine & session for PostgreSQL"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os
from dotenv import load_dotenv
load_dotenv()

# Environment variables
SQLALCHEMY_DB_URL = os.getenv('SQLALCHEMY_DATABASE_URL')

# Safeguard
if not SQLALCHEMY_DB_URL:
    raise ValueError("SQLALCHEMY_DATABASE_URL is not set")

# Create the SQLAlchemy engine (entry point to the database)
engine = create_engine(SQLALCHEMY_DB_URL)

# Create a SessionLocal class
# Each instance of SessionLocal will be a database session.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a base class
# Each ORM model (Python class) typically corresponds to a specific table in the database
Base = declarative_base()

# Dependency to get a DB session
'''
-> manages database sessions
-> provide a fresh database connection to each API request
-> ensure that the connection is closed afterward, even if an error occurs
-> Session: temporary, logical workspace that manages all interactions with a database for a specific task
'''
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()