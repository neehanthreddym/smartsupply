from app.database.mongo import conversation_logs, audit_logs
import datetime
import uuid
import sys

class LogService:
    @staticmethod
    def log_conversation_event(user_input: str, detected_intent: str, tool_chosen: str, tool_arguments: dict, tool_result_summary: str, status: str = "success", conversation_id: str = None):
        """
        Logs a user-agent interaction.
        """
        event = {
            "conversation_id": conversation_id or str(uuid.uuid4()),
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "user_input": user_input,
            "detected_intent": detected_intent,
            "tool_chosen": tool_chosen,
            "tool_arguments": tool_arguments,
            "tool_result_summary": tool_result_summary,
            "status": status
        }
        try:
            conversation_logs.insert_one(event)
        except Exception as e:
            # Fallback logging so we don't crash the app
            print(f"FAILED TO LOG CONVERSATION EVENT: {e}", file=sys.stderr)

    @staticmethod
    def log_inventory_event(action_type: str, product_sku: str, quantity_change: int, before_quantity: int, after_quantity: int, warehouse_name: str, reference_id: str = None):
        """
        Logs an inventory change (immutable audit record).
        """
        event = {
            "event_id": str(uuid.uuid4()),
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "action_type": action_type,
            "product_sku": product_sku,
            "warehouse": warehouse_name,
            "quantity_change": quantity_change,
            "before_quantity": before_quantity,
            "after_quantity": after_quantity,
            "reference_id": reference_id
        }
        try:
            audit_logs.insert_one(event)
        except Exception as e:
            print(f"FAILED TO LOG INVENTORY EVENT: {e}", file=sys.stderr)

    @staticmethod
    def log_error(context: str, error_message: str):
        """
        Generic error logger.
        """
        event = {
             "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
             "type": "ERROR",
             "context": context,
             "error_message": error_message
        }
        try:
            # Using conversation_logs as a catch-all for errors for now
            conversation_logs.insert_one(event)
        except Exception as e:
            print(f"FAILED TO LOG ERROR: {e}", file=sys.stderr)

    @staticmethod
    def log_catalog_event(entity_type: str, entity_id: str, action: str, details: dict):
        """
        Logs a catalog change (product/warehouse creation).
        """
        event = {
            "event_id": str(uuid.uuid4()),
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "action_type": f"create_{entity_type}",
            "entity_type": entity_type,
            "entity_id": entity_id,
            "action": action,
            "details": details
        }
        try:
            audit_logs.insert_one(event)
        except Exception as e:
            print(f"FAILED TO LOG CATALOG EVENT: {e}", file=sys.stderr)
