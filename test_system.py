from app.agents.rag_system import AgenticRAGSystem
import json

def test_queries():
    rag = AgenticRAGSystem()
    
    test_queries = [
        "Why was invoice INV-1023 flagged?",
        "Show me invoices from TechCorp",
        "Approve it"  # Follow-up query
    ]
    
    for query in test_queries:
        print(f"\n{'='*50}")
        print(f"Query: {query}")
        print('='*50)
        
        result = rag.process_query(query)
        print(f"Response: {result['response']}")
        print(f"Confidence: {result['confidence']}")
        print(f"Sources: {len(result['sources'])} documents")
        print("\nAudit Log:")
        for log in result['audit_log']:
            print(f"  - {log['step']}: {log['timestamp']}")

if __name__ == "__main__":
    test_queries()
