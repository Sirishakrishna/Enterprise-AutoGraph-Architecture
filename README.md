# 🕸️ Enterprise AutoGraph & Semantic Routing Architecture

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Neo4j](https://img.shields.io/badge/Neo4j-Graph_Database-018bff)
![LangChain](https://img.shields.io/badge/LangChain-Framework-green)
![Llama3](https://img.shields.io/badge/LLM-Llama_3.1-orange)
![License](https://img.shields.io/badge/License-MIT-purple)

## 📌 Overview: The Two Halves of Enterprise GraphRAG
This repository demonstrates a complete, production-grade Knowledge Graph architecture, solving the two biggest bottlenecks in Enterprise AI:
1. **The Ingestion Bottleneck:** Manually writing Cypher ETL pipelines for unstructured data.
2. **The Retrieval Danger:** Allowing LLMs to write dynamic, hallucination-prone database queries at runtime (Text-to-Cypher).

---

## 🏗️ Phase 1: LLM-Driven Ontology Extraction (`auto_extractor.py`)
In traditional architectures, data engineers write manual `CREATE` and `MERGE` queries. This collapses when dealing with thousands of unstructured PDFs. 

**The Solution:** We use a massive-parameter LLM (Llama-3.1 70B) as an automated Data Engineer. 
* The LLM reads unstructured English text.
* It dynamically extracts semantic Entities (Nodes) and their connections (Relationships) using strict schema guardrails.
* LangChain automatically translates the memory objects into optimized Cypher and pushes the topology directly into **Neo4j AuraDB**.

---

## 🔒 Phase 2: The Secure Semantic Router (`semantic_router.py`)
Once the graph is built, how do users query it? Relying on "Text-to-Cypher" in production is a massive security and reliability risk. LLMs will eventually hallucinate schema names or write broken syntax.

**The Solution: Intent-to-Template Routing.**
We completely strip the LLM of its coding privileges.
* **The LLM (Traffic Cop):** An ultra-fast LLM (Llama-3.1 8B) reads the user's question, classifies the **Intent**, extracts the **Entities**, and outputs strict JSON.
* **The Python Semantic Layer:** Python maps the JSON intent to a human-validated, hardcoded Cypher template. 
* **The Execution:** Neo4j safely executes the parameterized query. Result: **0% Syntax Errors. 0% Hallucinations.**

---

## 📂 Repository Structure
```text
├── src/                   
│   ├── auto_extractor.py  # Phase 1: LLM-driven ETL & Graph Construction
│   ├── semantic_router.py # Phase 2: Intent-to-Template Secure Retrieval
├── .env.example           # Configuration template
├── .gitignore             # Security and cache ignorance rules
├── requirements.txt       # Core dependencies
└── README.md              # Project documentation
