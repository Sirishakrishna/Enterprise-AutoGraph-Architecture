# 🕸️ Enterprise AutoGraph Architecture

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Neo4j](https://img.shields.io/badge/Neo4j-Graph_Database-018bff)
![LangChain](https://img.shields.io/badge/LangChain-Graph_Transformer-green)
![Llama3](https://img.shields.io/badge/LLM-Llama_3.1_70B-orange)
![License](https://img.shields.io/badge/License-MIT-purple)

## 📌 The Problem: The Cypher ETL Bottleneck
In traditional Knowledge Graph architectures, ingesting data requires Data Engineers to write complex, manual `CREATE` and `MERGE` Cypher queries. 

While this "baseline" approach works for highly structured CSVs, it completely collapses when an enterprise needs to build a graph from thousands of unstructured documents (SEC filings, medical records, legal contracts). Brute-forcing entity extraction and writing manual Cypher for a 50-page PDF is slow, expensive, and unscalable.

## 💡 The Solution: LLM-Driven Ontology Extraction
This repository demonstrates a production-grade **Auto-Graph Pipeline**. Instead of writing manual database queries, we use a massive-parameter LLM (Llama-3.1 70B) to act as an automated Data Engineer. 

The LLM reads unstructured English text, dynamically extracts semantic Entities (Nodes) and their connections (Relationships), and automatically pushes the resulting topological structure directly into Neo4j AuraDB.

### 🏗️ Architecture Flow
1. **Unstructured Ingestion:** Raw text is loaded into a LangChain `Document` object.
2. **LLM Graph Transformer:** Llama-3.1 parses the text, identifying grammatical subjects, objects, and predicates.
3. **Ontology Mapping:** The AI formats the extracted data into strict Node and Edge schema objects in memory.
4. **Auto-Cypher Execution:** The LangChain Neo4j wrapper translates the memory objects into optimized Cypher and executes the injection asynchronously.

## 📂 Repository Structure
```text
├── src/                   # Core Python application modules
│   ├── auto_extractor.py  # The LLM-driven ETL pipeline
├── .env.example           # Configuration template
├── .gitignore             # Security and cache ignorance rules
├── requirements.txt       # Core dependencies
└── README.md              # Project documentation