# app/models/schemas.py
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime

class InvoiceItem(BaseModel):
    description: str
    quantity: int
    unit_price: float
    total: float

class Invoice(BaseModel):
    invoice_id: str
    po_number: Optional[str]
    vendor: str
    invoice_date: str
    due_date: str
    total_amount: float
    currency: str
    status: str
    line_items: List[InvoiceItem]
    flagged_reasons: List[str]

class POItem(BaseModel):
    item_code: str
    description: str
    quantity_ordered: int
    quantity_received: int
    unit_price: float

class PurchaseOrder(BaseModel):
    po_number: str
    department: str
    created_date: str
    vendor: str
    total_amount: float
    currency: str
    status: str
    line_items: List[POItem]
    delivery_date: str
    approver: str

class QueryPlan(BaseModel):
    query_type: str
    entities: Dict[str, List[str]]
    search_strategy: Dict[str, Any]
    confidence: float
    reasoning: str
    timestamp: str
    original_query: str

class RetrievalResult(BaseModel):
    retrieved_docs: List[Dict[str, Any]]
    search_metadata: Dict[str, Any]
    confidence_score: float
    retrieval_strategy: str

class VerificationResult(BaseModel):
    verification_result: str
    confidence_score: float
    relevant_documents: List[int]
    missing_information: List[str]
    quality_assessment: Dict[str, float]
    recommendations: List[str]
    reasoning: str
    timestamp: str

class AuditEntry(BaseModel):
    timestamp: str
    action_type: str
    details: Dict[str, Any]
    session_id: str
