"""
SmartSupply Agent Example Usage.

Run this script to start an interactive chat with the inventory management agent.

Requirements:
1. Postgres database running with SmartSupply data
2. Ollama installed with a model (e.g., llama3.1)
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.database.postgres import get_db
from app.agent.agent_setup import create_smartsupply_agent, chat_loop


def main():
    """Initialize and run the SmartSupply agent."""
    
    print("🚀 Initializing SmartSupply AI Agent...")
    print("📦 Connecting to database...")
    
    # Get database session
    db = next(get_db())
    
    try:
        print("🤖 Loading Ollama model (llama3.1)...")
        
        # Create agent
        agent = create_smartsupply_agent(db, model_name="llama3.1:latest", temperature=0.1)
        
        print("✅ Agent ready!\n")
        
        # Example queries to try:
        print("Try asking:")
        print("  - List all products")
        print("  - List all warehouses")
        print("  - Show me products that are low on stock")
        print()
        
        # Start interactive chat
        chat_loop(agent)
        
    finally:
        db.close()
        print("Database connection closed.")


if __name__ == "__main__":
    main()