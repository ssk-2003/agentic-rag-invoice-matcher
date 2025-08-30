from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional
import uuid
from datetime import datetime
import re

# Import your modules
from models.schemas import QueryRequest, QueryResponse
from agents.planner import query_planner
from agents.retriever import DocumentRetriever
from agents.verifier import result_verifier
from data.vector_store import VectorStore, initialize_vector_store
from utils.audit import audit_logger
from utils.llm import llm_client

# Initialize FastAPI app
app = FastAPI(
    title="Agentic RAG Invoice Matcher",
    description="AI-powered invoice and PO matching system with multi-agent architecture",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables
vector_store = None
document_retriever = None

@app.on_event("startup")
async def startup_event():
    """Initialize the system when the app starts"""
    global vector_store, document_retriever
    
    print("🚀 Starting Agentic RAG Invoice Matcher...")
    
    # Initialize vector store with data
    vector_store = initialize_vector_store()
    
    # Initialize document retriever
    document_retriever = DocumentRetriever(vector_store)
    
    print("✅ System initialized successfully!")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Agentic RAG Invoice Matcher API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "components": {
            "vector_store": "operational" if vector_store else "not initialized",
            "retriever": "operational" if document_retriever else "not initialized"
        }
    }

@app.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """Main query processing endpoint - this is where the magic happens!"""
    
    if not document_retriever:
        raise HTTPException(status_code=503, detail="System not initialized")
    
    session_id = request.session_id or str(uuid.uuid4())
    
    try:
        # Step 1: Plan the query
        plan = query_planner.plan_query(request.query, session_id)
        
        # Initialize response
        response_data = {
            "answer": "",
            "evidence": [],
            "match_score": 0.0,
            "confidence": 0.0,
            "audit_log": [],
            "sources": []
        }
        
        # Step 2: Execute the plan
        invoice_data = None
        po_data = None
        
        # Extract IDs from query
        invoice_id = extract_invoice_id(request.query)
        po_number = extract_po_number(request.query)
        
        # Retrieve invoice data
        if "retrieve_invoice_data" in plan["steps"]:
            invoice_result = document_retriever.retrieve_invoice(request.query, invoice_id)
            if invoice_result["found"]:
                invoice_data = invoice_result["invoice"]
                response_data["evidence"].append({
                    "type": "invoice",
                    "data": invoice_data,
                    "confidence": invoice_result["confidence"]
                })
                response_data["sources"].append(f"Invoice {invoice_data['invoice_id']}")
        
        # Retrieve PO data
        if "retrieve_po_data" in plan["steps"]:
            po_result = document_retriever.retrieve_po(po_number, request.query)
            if po_result["found"]:
                po_data = po_result["po"]
                response_data["evidence"].append({
                    "type": "purchase_order", 
                    "data": po_data,
                    "confidence": po_result["confidence"]
                })
                response_data["sources"].append(f"PO {po_data['po_number']}")
        
        # Step 3: Verify and analyze
        if invoice_data and "analyze_flagging_reasons" in plan["steps"]:
            verification = result_verifier.verify_invoice_po_match(invoice_data, po_data)
            response_data["match_score"] = verification["match_score"]
            response_data["confidence"] = verification["confidence"]
            response_data["evidence"].append({
                "type": "verification",
                "data": verification,
                "confidence": verification["confidence"]
            })
        
        # Step 4: Generate response
        response_data["answer"] = generate_human_readable_response(
            request.query, invoice_data, po_data, response_data
        )
        
        # Step 5: Get audit logs for this session
        response_data["audit_log"] = audit_logger.get_recent_logs(5)
        
        return QueryResponse(**response_data)
    
    except Exception as e:
        audit_logger.log_action(
            agent_name="MainAPI",
            action="process_query_error",
            input_data={"query": request.query, "session_id": session_id},
            output_data={"error": str(e)},
            confidence=0
        )
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")

def extract_invoice_id(query: str) -> Optional[str]:
    """Extract invoice ID from query"""
    match = re.search(r'inv[-_]?(\d+)', query.lower())
    if match:
        return f"INV-{match.group(1)}"
    return None

def extract_po_number(query: str) -> Optional[str]:
    """Extract PO number from query"""
    match = re.search(r'po[-_]?(\d+)', query.lower())
    if match:
        return f"PO-{match.group(1)}"
    return None

def generate_human_readable_response(
    query: str, 
    invoice: Optional[Dict[str, Any]], 
    po: Optional[Dict[str, Any]], 
    response_data: Dict[str, Any]
) -> str:
    """Generate a human-readable response"""
    
    if not invoice:
        return "I couldn't find the specified invoice in our system. Please check the invoice number and try again."
    
    # Build response based on query type
    if "flagged" in query.lower():
        verification = None
        for evidence in response_data["evidence"]:
            if evidence["type"] == "verification":
                verification = evidence["data"]
                break
        
        if verification:
            answer = f"Invoice {invoice['invoice_id']} was flagged for the following reasons:\n\n"
            
            if verification["flagging_reasons"]:
                for i, reason in enumerate(verification["flagging_reasons"], 1):
                    answer += f"{i}. {reason}\n"
            
            answer += f"\nMatch Score: {verification['match_score']}/100\n"
            answer += f"Confidence Level: {verification['confidence']}%\n"
            
            if po:
                answer += f"\nComparison with PO {po['po_number']}:\n"
                answer += f"• Invoice Amount: ${invoice['amount']}\n"
                answer += f"• PO Amount: ${po['amount']}\n"
                answer += f"• Vendor: {invoice['vendor_name']}\n"
            
            if verification["recommendations"]:
                answer += f"\nRecommendations: {', '.join(verification['recommendations'])}"
            
            return answer
    
    # Default response
    answer = f"Found invoice {invoice['invoice_id']} from {invoice['vendor_name']} for ${invoice['amount']}."
    
    if po:
        answer += f" It's linked to PO {po['po_number']}."
        
    return answer

@app.get("/audit-logs")
async def get_audit_logs(limit: int = 20):
    """Get recent audit logs"""
    return audit_logger.get_recent_logs(limit)

@app.get("/invoices/{invoice_id}")
async def get_invoice(invoice_id: str):
    """Get specific invoice details"""
    if not vector_store:
        raise HTTPException(status_code=503, detail="System not initialized")
    
    invoice = vector_store.get_invoice_by_id(invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    return invoice

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
