import os
from dotenv import load_dotenv
load_dotenv()

import json
import chromadb
from langchain_community.embeddings import HuggingFaceEmbeddings  # LOCAL EMBEDDINGS
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from typing import List, Dict

class VectorStoreManager:
    def __init__(self, persist_directory: str = "./data/chroma_db"):
        self.persist_directory = persist_directory
        
        # USE LOCAL EMBEDDINGS - NO INTERNET REQUIRED
        self.embeddings = HuggingFaceEmbeddings(
            model_name="all-MiniLM-L6-v2"  # This downloads once and runs locally
        )
        print("✅ Using local embeddings (no internet required)")
        
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.invoice_store = None
        self.po_store = None

    def load_documents_from_json(self, file_path: str, doc_type: str) -> List[Document]:
        with open(file_path, 'r') as f:
            data = json.load(f)
        documents = []
        for item in data:
            if doc_type == "invoice":
                content = f"""
                Invoice ID: {item['invoice_id']}
                PO Number: {item.get('po_number', 'N/A')}
                Vendor: {item['vendor']}
                Total Amount: {item['total_amount']} {item['currency']}
                Status: {item['status']}
                Invoice Date: {item['invoice_date']}
                Due Date: {item['due_date']}
                
                Line Items:
                {chr(10).join([f"- {li['description']}: Qty {li['quantity']} @ ${li['unit_price']}" for li in item['line_items']])}
                
                Flagged Reasons: {', '.join(item.get('flagged_reasons', []))}
                """
            else:
                content = f"""
                PO Number: {item['po_number']}
                Department: {item['department']}
                Vendor: {item['vendor']}
                Total Amount: {item['total_amount']} {item['currency']}
                Status: {item['status']}
                Created Date: {item['created_date']}
                Delivery Date: {item['delivery_date']}
                
                Line Items:
                {chr(10).join([f"- {li['description']}: Ordered {li['quantity_ordered']}, Received {li['quantity_received']}" for li in item['line_items']])}
                
                Approver: {item['approver']}
                """
            doc = Document(
                page_content=content.strip(),
                metadata={
                    "type": doc_type,
                    "id": item.get('invoice_id' if doc_type == 'invoice' else 'po_number'),
                    "vendor": item['vendor'],
                    "amount": item['total_amount'],
                    "status": item['status']
                }
            )
            documents.append(doc)
        return documents

    def setup_vector_stores(self):
        invoice_docs = self.load_documents_from_json("data/invoices/mock_invoices.json", "invoice")
        self.invoice_store = Chroma.from_documents(
            documents=invoice_docs,
            embedding=self.embeddings,
            collection_name="invoices",
            persist_directory=self.persist_directory
        )
        po_docs = self.load_documents_from_json("data/pos/mock_pos.json", "po")
        self.po_store = Chroma.from_documents(
            documents=po_docs,
            embedding=self.embeddings,
            collection_name="pos",
            persist_directory=self.persist_directory
        )
        print("✅ Vector stores initialized successfully!")

    def get_invoice_retriever(self, k: int = 5):
        if not self.invoice_store:
            self.setup_vector_stores()
        return self.invoice_store.as_retriever(search_kwargs={"k": k})

    def get_po_retriever(self, k: int = 5):
        if not self.po_store:
            self.setup_vector_stores()
        return self.po_store.as_retriever(search_kwargs={"k": k})

if __name__ == "__main__":
    vs_manager = VectorStoreManager()
    vs_manager.setup_vector_stores()
    invoice_retriever = vs_manager.get_invoice_retriever()
    results = invoice_retriever.invoke("flagged invoice INV-1023")
    print(f"✅ Retrieved {len(results)} documents")
    for doc in results[:2]:
        print(f"Document: {doc.metadata}")
