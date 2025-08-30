from typing import Dict, Any, Optional
from utils.llm import llm_client
from utils.audit import audit_logger
import json

class ResultVerifier:
    """
    The Verifier checks if results make sense and determines confidence levels.
    This is like a quality control inspector.
    """
    
    def __init__(self):
        self.name = "ResultVerifier"
        self.confidence_threshold = 70  # Minimum confidence for auto-approval
    
    def verify_invoice_po_match(
        self, 
        invoice: Dict[str, Any], 
        po: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Verify if invoice matches PO and determine confidence"""
        
        audit_logger.log_action(
            agent_name=self.name,
            action="verify_match",
            input_data={"invoice_id": invoice.get("invoice_id"), "po_number": po.get("po_number") if po else None},
            output_data={},
            confidence=0
        )
        
        verification_result = {
            "match_score": 0,
            "confidence": 0,
            "issues": [],
            "recommendations": [],
            "flagging_reasons": [],
            "auto_approvable": False
        }
        
        try:
            # Use LLM for detailed analysis
            analysis = llm_client.analyze_invoice_po_match(invoice, po)
            
            verification_result.update(analysis)
            
            # Add rule-based checks
            if po:
                # Check vendor match
                if invoice.get("vendor_name", "").lower() != po.get("vendor_name", "").lower():
                    verification_result["issues"].append("Vendor name mismatch")
                    verification_result["match_score"] -= 20
                
                # Check amount (allow 5% variance)
                invoice_amount = float(invoice.get("amount", 0))
                po_amount = float(po.get("amount", 0))
                
                if abs(invoice_amount - po_amount) / po_amount > 0.05:
                    verification_result["issues"].append(f"Amount variance: Invoice ${invoice_amount}, PO ${po_amount}")
                    verification_result["match_score"] -= 15
                
                # Check PO number match
                if invoice.get("po_number") != po.get("po_number"):
                    verification_result["issues"].append("PO number mismatch")
                    verification_result["match_score"] -= 25
            
            else:
                verification_result["issues"].append("No matching purchase order found")
                verification_result["match_score"] = 30
                verification_result["flagging_reasons"].append("Missing PO reference")
            
            # Determine flagging reasons
            if verification_result["match_score"] < 70:
                verification_result["flagging_reasons"].extend(verification_result["issues"])
            
            # Set confidence based on match score and issues
            verification_result["confidence"] = max(0, min(100, 
                verification_result["match_score"] - len(verification_result["issues"]) * 5))
            
            # Auto-approval logic
            verification_result["auto_approvable"] = (
                verification_result["confidence"] >= self.confidence_threshold and
                len(verification_result["issues"]) <= 1
            )
            
            # Add recommendations
            if verification_result["confidence"] < 50:
                verification_result["recommendations"].append("Manual review required")
            elif verification_result["confidence"] < 80:
                verification_result["recommendations"].append("Secondary approval recommended")
            else:
                verification_result["recommendations"].append("Suitable for auto-approval")
        
        except Exception as e:
            verification_result["error"] = str(e)
            verification_result["confidence"] = 0
            verification_result["issues"].append(f"Verification error: {str(e)}")
        
        # Log results
        audit_logger.log_action(
            agent_name=self.name,
            action="verify_complete",
            input_data={"invoice_id": invoice.get("invoice_id"), "po_number": po.get("po_number") if po else None},
            output_data=verification_result,
            confidence=verification_result["confidence"]
        )
        
        return verification_result
    
    def should_escalate(self, confidence: float, issues: List[str]) -> bool:
        """Determine if case should be escalated to human review"""
        return confidence < self.confidence_threshold or len(issues) > 2

# Global verifier instance
result_verifier = ResultVerifier()
