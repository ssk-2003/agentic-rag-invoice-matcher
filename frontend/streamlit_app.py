import streamlit as st
import json
import sys
import os

# Add the parent directory to Python path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.agents.rag_system import AgenticRAGSystem

# Initialize the RAG system
@st.cache_resource
def load_rag_system():
    return AgenticRAGSystem()

def main():
    st.set_page_config(page_title="Agentic RAG Invoice Matcher", layout="wide")
    
    st.title("🤖 Agentic RAG Invoice Matcher")
    st.markdown("*AI-powered invoice and PO matching system with audit logging*")
    
    # Initialize system
    rag = load_rag_system()
    
    # Sidebar for system info
    with st.sidebar:
        st.header("📊 System Status")
        st.success("✅ Vector Store: Ready")
        st.success("✅ Local Embeddings: Loaded")
        st.success("✅ Rule-based LLM: Active")
        
        st.header("🔍 Sample Queries")
        sample_queries = [
            "Why was invoice INV-1023 flagged?",
            "Show me invoices from TechCorp",
            "Find PO-2025 details",
            "Approve it"
        ]
        
        for query in sample_queries:
            if st.button(query, key=f"btn_{query}"):
                st.session_state.query = query
    
    # Main query interface
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("💬 Query Interface")
        
        # Get query from session state or text input
        query = st.text_input(
            "Ask about invoices, POs, or flagged items:",
            value=st.session_state.get('query', ''),
            placeholder="e.g., Why was invoice INV-1023 flagged?"
        )
        
        if st.button("🔍 Process Query", type="primary"):
            if query:
                with st.spinner("Processing query..."):
                    try:
                        # Process the query
                        result = rag.process_query(query)
                        
                        # Display response
                        st.subheader("📝 Response")
                        st.markdown(result['response'])
                        
                        # Display metrics
                        col_conf, col_sources = st.columns(2)
                        with col_conf:
                            st.metric("Confidence", f"{result['confidence']:.1%}")
                        with col_sources:
                            st.metric("Sources Found", len(result['sources']))
                        
                        # Store in session for audit log
                        st.session_state.last_result = result
                        
                    except Exception as e:
                        st.error(f"Error processing query: {e}")
    
    with col2:
        st.header("📋 Retrieved Sources")
        
        if 'last_result' in st.session_state:
            result = st.session_state.last_result
            
            # Show sources
            if result['sources']:
                for i, source in enumerate(result['sources'][:3]):
                    with st.expander(f"📄 {source.get('type', 'document').title()} {source.get('id', f'#{i+1}')}"):
                        st.write(f"**Vendor:** {source.get('vendor', 'Unknown')}")
                        st.write(f"**Amount:** ${source.get('amount', 'Unknown')}")
                        st.write(f"**Status:** {source.get('status', 'Unknown')}")
            else:
                st.info("No sources retrieved")
    
    # Audit Log Section
    if 'last_result' in st.session_state:
        st.header("🔍 Audit Log")
        
        result = st.session_state.last_result
        
        # Show audit log
        audit_data = []
        for log_entry in result['audit_log']:
            audit_data.append({
                "Step": log_entry['step'].replace('_', ' ').title(),
                "Timestamp": log_entry['timestamp'],
                "Details": str(log_entry.get('output', log_entry.get('retrieved_count', 'Completed')))
            })
        
        if audit_data:
            st.dataframe(audit_data, use_container_width=True)
        
        # Show raw JSON (collapsible)
        with st.expander("🔧 Raw Response JSON"):
            st.json(result)

if __name__ == "__main__":
    main()
