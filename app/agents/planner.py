import re
from datetime import datetime

class QueryPlanner:
    def __init__(self):
        # NO OPENAI - pure rule-based planning
        pass
        
    def plan_query(self, user_query: str) -> dict:
        """Analyze user query and determine what actions to take"""
        
        # Extract invoice ID if present
        invoice_match = re.search(r'INV-(\d+)', user_query.upper())
        invoice_id = invoice_match.group(0) if invoice_match else None
        
        # Simple rule-based planning
        plan = {
            "query": user_query,
            "invoice_id": invoice_id,
            "actions": [],
            "timestamp": datetime.now().isoformat(),
            "reasoning": ""
        }
        
        if "flagged" in user_query.lower() or "flag" in user_query.lower():
            plan["actions"].append("retrieve_invoice")
            if invoice_id:
                plan["actions"].append("retrieve_matching_po")
            plan["actions"].append("explain_flagging")
            plan["reasoning"] = f"User asking about flagged invoice {invoice_id}"
            
        elif "approve" in user_query.lower():
            plan["actions"].append("approve_invoice")
            plan["reasoning"] = "User requesting invoice approval"
            
        else:
            plan["actions"].append("general_search")
            plan["reasoning"] = "General invoice/PO search query"
            
        return plan

if __name__ == "__main__":
    planner = QueryPlanner()
    result = planner.plan_query("Why was invoice INV-1023 flagged?")
    print("Planning result:", result)
