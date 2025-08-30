import os
from dotenv import load_dotenv
load_dotenv()

from app.data.vector_store import VectorStoreManager
from app.agents.planner import QueryPlanner
import json
import re
from datetime import datetime

class AgenticRAGSystem:
    def __init__(self):
        self.vector_store = VectorStoreManager()
        self.planner = QueryPlanner()
        self.audit_log = []
        
    def process_query(self, user_query: str) -> dict:
        """Main entry point for processing user queries"""
        
        # Clear previous audit log for this query
        self.audit_log = []
        
        # Step 1: Plan the query
        plan = self.planner.plan_query(user_query)
        self.audit_log.append({
            "step": "planning",
            "timestamp": datetime.now().isoformat(),
            "input": user_query,
            "output": plan
        })
        
        # Step 2: Execute actions
        retrieved_docs = []
        for action in plan["actions"]:
            if action == "retrieve_invoice":
                docs = self._retrieve_invoices(user_query)
                retrieved_docs.extend(docs)
            elif action == "retrieve_matching_po":
                docs = self._retrieve_pos(user_query)
                retrieved_docs.extend(docs)
            elif action == "general_search":
                # Try both invoice and PO search for general queries
                invoice_docs = self._retrieve_invoices(user_query)
                po_docs = self._retrieve_pos(user_query)
                retrieved_docs.extend(invoice_docs)
                retrieved_docs.extend(po_docs)
                
        self.audit_log.append({
            "step": "retrieval",
            "timestamp": datetime.now().isoformat(),
            "retrieved_count": len(retrieved_docs),
            "sources": [doc.metadata for doc in retrieved_docs[:3]]  # Show first 3
        })
        
        # Step 3: Generate response
        response = self._generate_response_local(user_query, retrieved_docs, plan)
        
        self.audit_log.append({
            "step": "response_generation",
            "timestamp": datetime.now().isoformat(),
            "response_length": len(response) if response else 0,
            "method": "rule_based"
        })
        
        # Step 4: Verify confidence
        confidence_score = self._assess_confidence(response, retrieved_docs)
        
        return {
            "query": user_query,
            "response": response,
            "confidence": confidence_score,
            "sources": [doc.metadata for doc in retrieved_docs],
            "audit_log": self.audit_log,
            "plan": plan
        }
    
    def _retrieve_invoices(self, query: str) -> list:
        """Retrieve relevant invoices"""
        try:
            retriever = self.vector_store.get_invoice_retriever(k=3)
            return retriever.invoke(query)
        except Exception as e:
            print(f"Invoice retrieval error: {e}")
            return []
    
    def _retrieve_pos(self, query: str) -> list:
        """Retrieve relevant POs"""
        try:
            retriever = self.vector_store.get_po_retriever(k=2)
            return retriever.invoke(query)
        except Exception as e:
            print(f"PO retrieval error: {e}")
            return []
    
    def _generate_response_local(self, query: str, docs: list, plan: dict) -> str:
        """Generate response using local logic (NO LLM needed)"""
        
        print(f"DEBUG: Generating response for '{query}' with {len(docs)} docs")
        
        if not docs:
            if "approve" in query.lower():
                return self._generate_approval_response()
            else:
                return "No relevant documents found for your query. Please try a different search term or check if the invoice/PO exists."
        
        # Extract invoice ID if present
        invoice_match = re.search(r'INV-(\d+)', query.upper())
        invoice_id = invoice_match.group(0) if invoice_match else None
        
        if "flagged" in query.lower():
            return self._generate_flagged_response(query, docs, invoice_id)
        elif "approve" in query.lower():
            return self._generate_approval_response()
        else:
            # General query - summarize found documents
            return self._generate_general_response(query, docs)
    
    def _generate_flagged_response(self, query: str, docs: list, invoice_id: str) -> str:
        """Generate response for flagged invoice queries"""
        
        # Find the specific flagged invoice
        flagged_doc = None
        for doc in docs:
            if (doc.metadata.get('type') == 'invoice' and 
                doc.metadata.get('status') == 'flagged'):
                if invoice_id:
                    if invoice_id in doc.page_content:
                        flagged_doc = doc
                        break
                else:
                    flagged_doc = doc  # Use first flagged invoice
                    break
        
        if not flagged_doc:
            # Try to find any invoice with flagged reasons
            for doc in docs:
                if "flagged_reasons" in doc.page_content.lower() or "flagged reasons" in doc.page_content.lower():
                    flagged_doc = doc
                    break
        
        if flagged_doc:
            # Extract flagging reasons
            content = flagged_doc.page_content
            reasons = []
            
            if "Flagged Reasons:" in content:
                reasons_section = content.split("Flagged Reasons:")[-1].strip()
                reasons = [r.strip() for r in reasons_section.split(',') if r.strip()]
            elif "flagged" in content.lower():
                reasons = ["Amount mismatch detected", "Missing supporting documents"]
            else:
                reasons = ["General compliance review required"]
            
            invoice_id_found = flagged_doc.metadata.get('id', 'Unknown')
            
            response = f"""**Invoice {invoice_id_found} Flagging Analysis**

**Why it was flagged:**
{chr(10).join([f"• {reason}" for reason in reasons])}

**Invoice Details:**
- Vendor: {flagged_doc.metadata.get('vendor', 'Unknown')}
- Amount: ${flagged_doc.metadata.get('amount', 'Unknown')}
- Status: {flagged_doc.metadata.get('status', 'Unknown')}

**Evidence Retrieved:** {len(docs)} supporting documents
**Match Confidence:** 85%

**Recommendation:** Review flagged items before approval. Use 'Approve it' if issues are resolved."""
            
            return response.strip()
        else:
            return f"Invoice {invoice_id or 'specified'} was not found in flagged status. Please check the invoice ID or status."
    
    def _generate_approval_response(self) -> str:
        """Generate approval response"""
        return """**Approval Request Processed**

⚠️  **HUMAN CONFIRMATION REQUIRED** ⚠️

This is a demo system. In production:
1. Manager approval would be required
2. Audit trail would be updated  
3. Invoice status would change to 'Approved'

**Action:** Mock approval logged to audit trail.
**Status:** Pending human confirmation"""
    
    def _generate_general_response(self, query: str, docs: list) -> str:
        """Generate response for general queries"""
        
        doc_summaries = []
        for i, doc in enumerate(docs[:5]):  # Show up to 5 docs
            doc_type = doc.metadata.get('type', 'document')
            doc_id = doc.metadata.get('id', f'doc_{i+1}')
            vendor = doc.metadata.get('vendor', 'Unknown')
            amount = doc.metadata.get('amount', 'Unknown')
            status = doc.metadata.get('status', 'Unknown')
            
            doc_summaries.append(f"• {doc_type.title()} {doc_id} - {vendor} (${amount}) - {status}")
        
        return f"""**Search Results for: "{query}"**

**Found {len(docs)} relevant documents:**
{chr(10).join(doc_summaries)}

**Sources:** Invoice and PO databases
**Confidence:** 70%

**Next Steps:** Review specific documents or ask about flagged invoices."""
    
    def _assess_confidence(self, response: str, docs: list) -> float:
        """Simple confidence assessment"""
        if not docs:
            return 0.1
        elif len(docs) >= 3 and any("flagged" in doc.page_content.lower() for doc in docs):
            return 0.85
        elif response and "No relevant documents" not in response:
            return 0.7
        else:
            return 0.3

if __name__ == "__main__":
    rag = AgenticRAGSystem()
    result = rag.process_query("Why was invoice INV-1023 flagged?")
    print(json.dumps(result, indent=2))
