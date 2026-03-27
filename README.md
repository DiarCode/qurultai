<div align="center">

# Qurultai AI

### The Digital Council for Transparent Governance

[![Status](https://img.shields.io/badge/Status-MVP_Ready-brightgreen)]()
[![Framework](https://img.shields.io/badge/Framework-LangGraph-blue)]()
[![Frontend](https://img.shields.io/badge/Frontend-Vue.js_3-42b883)]()
[![Backend](https://img.shields.io/badge/Backend-FastAPI-009688)]()
[![License](https://img.shields.io/badge/License-MIT-blue.svg)]()

</div>

---

## 📜 Executive Summary

**Qurultai** is a sovereign, multi-agent decision support platform designed to modernize public administration. Named after the ancient Turkic council of leaders, Qurultai simulates a "Digital Cabinet" where AI agents represent specific government ministries.

These agents analyze policy documents, detect conflicts between legal frameworks, and collaborate to generate consensus-based recommendations. It transforms the opaque, siloed process of government decision-making into a transparent, auditable, and efficient digital workflow.

## 🔥 The Problem

Government decision-making is plagued by **Institutional Fragmentation**:

- **Siloed Data:** Ministries operate independently; decisions by one often violate the regulations of another.
- **Opacity:** Citizens and businesses often cannot understand _why_ a decision was made or which laws apply.
- **Latency:** Inter-ministerial coordination is manual, paper-based, and slow.

## 💡 The Solution

Qurultai introduces an **Agentic Orchestration Layer** over government data.

1.  **Input:** A user (Citizen, Business, or Official) submits a query or document.
2.  **Council:** Specialized AI agents (Finance, Justice, Ecology) analyze the input against their specific legal knowledge bases.
3.  **Debate:** Agents identify conflicts and propose solutions in a transparent "Group Chat" format.
4.  **Consensus:** A Synthesizer agent compiles the debate into a structured, legally referenced PDF report.

## 🚀 Key Features

- **The Council Chamber:** A unique chat interface where users observe AI agents debating and collaborating in real-time.
- **Agent Orchestration Panel:** An admin dashboard to create, configure, and deploy specialized agents (e.g., assign "Tax Code" to the Finance Agent).
- **Sovereign RAG Engine:** Retrieval-Augmented Generation runs locally using Ollama, ensuring sensitive government data never leaves the infrastructure.
- **Explainable AI:** Every decision is traced back to specific articles in the law. No "Black Box" answers.
- **PDF Report Generation:** Automatic creation of official-style documents for government circulation.

## 🛠️ Tech Stack & Architecture

This project uses a modular, sovereignty-first architecture:

| Component         | Technology                                   |
| :---------------- | :------------------------------------------- |
| **Orchestration** | LangGraph (State Machine for Cyclic Debates) |
| **Frontend**      | Vue.js 3 + Vite + PrimeVue                   |
| **Backend**       | FastAPI (Python)                             |
| **Local LLM**     | Ollama (Llama 3 / Mistral)                   |
| **Vector Store**  | ChromaDB                                     |
| **Database**      | SQLite                                       |
| **Embeddings**    | Nomic Embed Text (via Ollama)                |

### Architecture Flow

```mermaid
graph LR
    A[Vue.js Client] --> B[FastAPI Gateway]
    B --> C{LangGraph Router}
    C --> D[Agent: Finance]
    C --> E[Agent: Ecology]
    C --> F[Agent: Justice]
    D --> G[ChromaDB RAG]
    E --> G
    F --> G
    D <--> H[Debate Loop]
    E <--> H
    F <--> H
    H --> I[Synthesizer Agent]
    I --> J[Final Report PDF]
```

````

## 📂 Project Structure

```
qurultai/
├── backend/
│   ├── agents/           # LangGraph logic & Agent definitions
│   ├── core/             # Config, LLM loaders (Ollama)
│   ├── tools/            # RAG retrieval, PDF generation
│   ├── models/           # SQLite database models
│   └── main.py           # FastAPI entry point
├── frontend/
│   ├── src/
│   │   ├── components/   # Vue components (Chat, Agent Card)
│   │   ├── views/        # Pages (Council, Admin)
│   │   └── stores/       # Pinia state management
├── data/
│   └── documents/        # Uploaded PDF storage
└── README.md
```

## ⚡ Getting Started (Installation)

Follow these steps to run the MVP locally.

### Prerequisites

- Python 3.10+
- Node.js 18+
- [Ollama](https://ollama.com/) installed and running

### 1. Setup LLM (Ollama)

```bash
# Pull the model
ollama pull llama3

# Pull the embedding model
ollama pull nomic-embed-text
```

### 2. Setup Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Start FastAPI server
uvicorn main:app --reload
```

### 3. Setup Frontend

```bash
cd frontend
npm install
npm run dev
```

Access the application at `http://localhost:5173`.

## 🎬 Demo Use Cases

### Case 1: Land Allocation Conflict

- **Input:** "I want to build a chemical plant 200m from the river."
- **Process:** Economy Agent (Approves for revenue) vs. Ecology Agent (Rejects for code violation).
- **Resolution:** Agents find a legal exception allowing construction if "Zero Liquid Discharge" technology is used.

### Case 2: Business Compliance

- **Input:** "What permits do I need to open a pharmacy?"
- **Process:** Health Agent (License), Tax Agent (Regime), Fire Safety Agent (Norms).
- **Output:** A consolidated checklist with citations.

## 🗺️ Roadmap

- [x] Core LangGraph Debate Loop
- [x] Vue.js Council Chamber UI
- [x] Ollama Integration
- [ ] Dynamic Agent Creation via UI
- [ ] WebSocket Streaming for real-time typing effect
- [ ] Multi-language support (Kazakh/Russian/English)

## 🤝 Team

Built for **Decentrathon 5.0 - AI for Government Track**.

<div align="center">
  <i>Qurultai: Where Tradition Meets Digital Intelligence.</i>
</div>
````
