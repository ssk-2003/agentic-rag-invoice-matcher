# Agentic RAG Invoice Matcher

An end-to-end AI-powered pipeline to answer and audit invoice/PO questions using Retrieval-Augmented Generation (RAG).

## 🚀 Quick Start

1. **Clone the repo:**

git clone https://github.com/ssk-2003/agentic-rag-invoice-matcher.git
cd agentic-rag-invoice-matcher

text

2. **Setup Environment:**
python -m venv venv
venv\Scripts\activate # Or 'source venv/bin/activate' on Linux/Mac
pip install -r requirements.txt

text

3. **Prepare Data & Vector Store:**
python app/data/mock_invoices.py
python app/data/vector_store.py

text

4. **Run Tests/Demo:**
python test_system.py

text

5. **(Optional) Start Web Dashboard:**
pip install streamlit
streamlit run app/frontend/streamlit_app.py

text

## 📅 Architecture Diagram

*(Insert architecture_diagram.png or a drawing of your component flow here)*

## 🗂️ Files & Folders

| File/Folder             | Purpose                                            |
|-------------------------|---------------------------------------------------|
| `app/agents/planner.py` | Simple rule-based planner for action selection     |
| `app/agents/rag_system.py` | Orchestrates all agents and produces answers  |
| `app/data/mock_invoices.py` | Creates demo invoices and PO data           |
| `app/data/vector_store.py` | Builds vector search database for retrieval   |
| `test_system.py`        | CLI test/demo of the main system                  |
| `requirements.txt`      | All dependencies                                  |
| `README.md`             | This documentation                                |

## ⚠️ Limitations

- No real-world API or LLM connection (demo is 100% local, rule-based)
- Uses mock invoices and PO (demo data)
- Simple retriever, planner, and audit trail logic (ideal for interview/demo)

## ✅ Provenance & Audit🏗️ AGENTIC RAG ARCHITECTURE - INVOICE MATCHER

┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ User Query  │───▶│   Planner   │───▶│ Retrieval   │───▶│  Verifier & │
│   Input     │    │(Rule-Based) │    │   Agents    │    │ Confidence  │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
                           │                   │                   │
                           │                   ▼                   ▼
┌─────────────┐           │          ┌─────────────┐    ┌─────────────┐
│ Audit Log   │◀──────────┼──────────│ Vector      │    │ Response    │
│ (JSON)      │           │          │ Stores      │    │Synthesizer  │
└─────────────┘           │          │(Invoice+PO) │    └─────────────┘
                          │          └─────────────┘           │
                          │                                   ▼
                          └──────────────────────────┌─────────────┐
                                                     │ Final       │
                                                     │ Response    │
                                                     └─────────────┘

COMPONENTS:
• User Query: Invoice/PO questions
• Planner: Determines retrieval strategy  
• Retrieval Agents: Vector search in invoice/PO databases
• Verifier: Confidence scoring & validation
• Response Synthesizer: Human-readable answer generation
• Audit Log: Complete pipeline tracking (JSON format)




