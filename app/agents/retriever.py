from typing import Dict, Any, List, Optional
from data.vector_store import VectorStore
from utils.audit import audit_logger
import json

class DocumentRetriever:
    """
    The Retriever finds relevant invoices and POs from the database.
    This is like a smart search engine for your documents.
    """
    
    def __init__(self, vector_store: VectorStore):
        self.name = "DocumentRetriever"
        self.vector_store = vector_store
    
    def retrieve_invoice(self, query: str, invoice_id: str = None) -> Dict[str, Any]:
        """Retrieve invoice information"""
        
        audit_logger.log_action(
            agent_name=self.name,
            action="retrieve_invoice",
            input_data={"query": query, "invoice_id": invoice_id},
            output_data={},
            confidence=0
        )
        
        results = {
            "found": False,
            "invoice": None,
            "confidence": 0,
            "search_results": []
        }
        
        try:
            if invoice_id:
                # Direct lookup by ID
                invoice = self.vector_store.get_invoice_by_id(invoice_id)
                if invoice:
                    results["found"] = True
                    results["invoice"] = invoice
                    results["confidence"] = 95
            
            if not results["found"]:
                # Search by query
                search_results = self.vector_store.search_invoices(query, n_results=3)
                if search_results["metadatas"] and len(search_results["metadatas"]) > 0:
                    results["found"] = True
                    results["invoice"] = search_results["metadatas"][0]
                    results["search_results"] = search_results["metadatas"]
                    results["confidence"] = 80
        
        except Exception as e:
            results["error"] = str(e)
            results["confidence"] = 0
        
        # Log results
        audit_logger.log_action(
            agent_name=self.name,
            action="retrieve_invoice_complete",
            input_data={"query": query, "invoice_id": invoice_id},
            output_data=results,
            confidence=results["confidence"]
        )
        
        return results
    
    def retrieve_po(self, po_number: str = None, query: str = "") -> Dict[str, Any]:
        """Retrieve purchase order information"""
        
        audit_logger.log_action(
            agent_name=self.name,
            action="retrieve_po",
            input_data={"po_number": po_number, "query": query},
            output_data={},
            confidence=0
        )
        
        results = {
            "found": False,
            "po": None,
            "confidence": 0,
            "search_results": []
        }
        
        try:
            if po_number:
                # Direct lookup by PO number
                po = self.vector_store.get_po_by_number(po_number)
                if po:
                    results["found"] = True
                    results["po"] = po
                    results["confidence"] = 95
            
            if not results["found"] and query:
                # Search by query
                search_results = self.vector_store.search_pos(query, n_results=3)
                if search_results["metadatas"] and len(search_results["metadatas"]) > 0:
                    results["found"] = True
                    results["po"] = search_results["metadatas"][0]
                    results["search_results"] = search_results["metadatas"]
                    results["confidence"] = 75
        
        except Exception as e:
            results["error"] = str(e)
            results["confidence"] = 0
        
        # Log results
        audit_logger.log_action(
            agent_name=self.name,
            action="retrieve_po_complete",
            input_data={"po_number": po_number, "query": query},
            output_data=results,
            confidence=results["confidence"]
        )
        
        return results

# This will be initialized in main.py
document_retriever = None
