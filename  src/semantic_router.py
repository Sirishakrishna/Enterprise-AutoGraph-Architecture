import os
import json
import logging
from dotenv import load_dotenv
from neo4j import GraphDatabase
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser

# Load hidden keys securely
load_dotenv()

# Configure enterprise logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ==========================================
# THE ENTERPRISE SEMANTIC LAYER (CYPHER TEMPLATES)
# We human-validate these queries. The LLM never writes Cypher!
# ==========================================
CYPHER_TEMPLATES = {
    "find_ceo": """
        MATCH (p:Person)-[:CEO_OF]->(c:Company {id: $company_name}) 
        RETURN p.id AS answer
    """,
    "find_tech_created": """
        MATCH (c:Company {id: $company_name})-[:CREATED]->(t:Technology) 
        RETURN t.id AS answer
    """,
    "unknown": ""
}

def execute_safe_cypher(intent: str, parameters: dict):
    """Executes a pre-validated Cypher template safely."""
    if intent not in CYPHER_TEMPLATES or intent == "unknown":
        return "I'm sorry, I don't have a secure template to answer that question."
        
    query = CYPHER_TEMPLATES[intent]
    
    # Connect to Neo4j
    driver = GraphDatabase.driver(
        os.getenv("NEO4J_URI"), 
        auth=(os.getenv("NEO4J_USER"), os.getenv("NEO4J_PASSWORD"))
    )
    
    with driver.session(database=os.getenv("NEO4J_DATABASE", "neo4j")) as session:
        result = session.run(query, **parameters)
        answers = [record["answer"] for record in result]
        
    driver.close()
    return answers if answers else "No data found in the Knowledge Graph."

if __name__ == "__main__":
    logger.info("Starting Enterprise Semantic Router (Intent-to-Template)...")

    # 1. The User's Question
    user_question = "Can you tell me who the CEO of Visa Inc. is?"
    logger.info(f"USER QUESTION: {user_question}")

    try:
        # 2. Initialize the LLM (Using 8B for lightning-fast JSON extraction)
        llm = ChatGroq(
            groq_api_key=os.getenv("GROQ_API_KEY"),
            model_name="llama-3.1-8b-instant",
            temperature=0 
        )

        # 3. Prompt Engineering: Force the LLM to output STRICT JSON only
        parser = JsonOutputParser()
        prompt = PromptTemplate(
            template="""
            You are a strict API routing agent. Your ONLY job is to analyze the user's question, 
            determine their intent, and extract the company name.
            
            Allowed Intents: ['find_ceo', 'find_tech_created', 'unknown']
            
            User Question: {question}
            
            You must respond with ONLY a valid JSON object matching this format:
            {{
                "intent": "the_allowed_intent",
                "company_name": "Exact Name of Company"
            }}
            """,
            input_variables=["question"],
        )

        # 4. The LLM Routing Chain (No Cypher generation allowed!)
        logger.info("Routing question through LLM for Intent Classification...")
        chain = prompt | llm | parser
        
        # ⚡ The LLM reads the question and outputs a JSON dictionary
        llm_extraction = chain.invoke({"question": user_question})
        
        print("\n" + "="*50)
        print(f"🧠 LLM JSON EXTRACTION: {json.dumps(llm_extraction, indent=2)}")
        print("="*50)

        # 5. Execute the Safe, Hardcoded Cypher Template
        intent = llm_extraction.get("intent")
        company_name = llm_extraction.get("company_name")
        
        logger.info(f"Mapping Intent '{intent}' to secure Cypher Template...")
        
        # Pass the extracted parameters safely to the database
        db_results = execute_safe_cypher(intent, {"company_name": company_name})
        
        print("\n" + "="*50)
        print(f"🔒 SECURE DATABASE RESULT: {db_results[0]}")
        print("="*50 + "\n")

    except Exception as e:
        logger.error(f"Pipeline failed: {str(e)}")