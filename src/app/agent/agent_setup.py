"""
SmartSupply Agent Setup (LangChain v1 create_agent).
"""

from sqlalchemy.orm import Session
from langchain_ollama import ChatOllama
from langchain.agents import create_agent


def create_smartsupply_agent(
    db: Session,
    model_name: str = "llama3.1",
    temperature: float = 0.1,
):
    """
    Create a SmartSupply inventory management agent.
    
    Args:
        db: Database session for tool access
        model_name: Ollama model name (default: llama3.1)
        temperature: LLM temperature (0-1, lower = more focused)
    
    Returns:
        
    """
    
    # Import tools
    from app.tools.langchain_tools import create_inventory_tools
    
    # Create all 12 tools
    tools = create_inventory_tools(db)
    
    # Initialize LLM
    llm = ChatOllama(
        model=model_name,
        temperature=temperature,
    )
    
    # Create system prompt
    system_prompt = """You are SmartSupply AI, an intelligent inventory management assistant.

You have access to 12 tools organized by permission level:

📖 READ-ONLY (6 tools) - Use freely:
  - query_inventory_stock
  - query_inventory_details
  - query_low_stock_items
  - query_movement_history
  - query_product_catalog
  - query_warehouse_catalog

⚠️ SOFT GATE (3 tools) - Ask for awareness confirmation:
  - create_product
  - create_warehouse
  - adjust_inventory_inbound

🚨 HARD GATE (3 tools) - Require strict confirmation:
  - report_inventory_anomaly
  - adjust_inventory_outbound
  - transfer_inventory

IMPORTANT RULES:
1. For SOFT GATE tools: Say "I can do this, should I proceed?" and wait for confirmation
2. For HARD GATE tools: Explain the impact and say "This requires your explicit approval. Confirm?" and wait
3. Never execute soft/hard gate tools without user confirmation
4. Be conversational and helpful
5. Explain what you're doing in simple terms

Your goal is to help users manage inventory efficiently and safely."""    
    # Create agent
    agent = create_agent(
        model=llm, 
        tools=tools,
        system_prompt=system_prompt
    )
    
    return agent


def chat_loop(agent):
    """
    Simple interactive chat loop for the agent.
    
    Args:
        agent: Configured Agent
    """
    print("\n" + "="*60)
    print("SmartSupply AI Agent - Type 'exit' to quit")
    print("="*60 + "\n")

    messages = []
    
    while True:
        try:
            user_input = input("\nYou: ").strip()
            
            if user_input.lower() in ['exit', 'quit', 'q']:
                print("\nGoodbye! 👋")
                break
            if not user_input:
                continue

            messages.append({"role": "user", "content": user_input})

            # Invoke agent
            state = agent.invoke({"messages": messages})
            messages = state["messages"]

            latest = messages[-1]
            if getattr(latest, "content", None):
                print(f"\nAgent: {latest.content}")
            elif getattr(latest, "tool_calls", None):
                print(f"\nAgent is calling tools: {[tc['name'] for tc in latest.tool_calls]}")
            
        except KeyboardInterrupt:
            print("\n\nGoodbye! 👋")
            break
        except Exception as e:
            print(f"\nError: {str(e)}")