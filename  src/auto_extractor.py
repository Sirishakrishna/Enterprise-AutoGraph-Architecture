import os
import logging
from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_groq import ChatGroq
from langchain_experimental.graph_transformers import LLMGraphTransformer
from langchain_neo4j import Neo4jGraph

# Load hidden keys securely
load_dotenv()

# Configure enterprise logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info("Starting Enterprise Auto-Graph Extraction Pipeline...")

    # 1. Unstructured Data (A complex, messy corporate announcement)
    unstructured_text = """
    Visa Inc., headquartered in San Francisco, recently announced a strategic partnership with Databricks. 
    Databricks is a leading AI company founded by Matei Zaharia, who also created Apache Spark. 
    Ryan McInerney, the CEO of Visa, stated that the partnership will focus on building Data Intelligence Platforms. 
    These platforms will utilize MLflow, another open-source technology developed by Databricks, 
    to enhance Visa's global fraud detection systems.
    """
    
    docs = [Document(page_content=unstructured_text)]
    logger.info("Unstructured corporate document loaded into memory.")

    try:
        # 2. Initialize the LLM (Using the lightning-fast Llama-3.1 8B)
        logger.info("Initializing the Llama-3.1 8B extraction engine...")
        llm = ChatGroq(
            groq_api_key=os.getenv("GROQ_API_KEY"),
            model_name="llama-3.1-8b-instant",  # <-- The new active model!
            temperature=0 # Zero creativity = zero hallucinations
        )

        # 3. Initialize the Graph Transformer with Strict Schema Guardrails
        logger.info("Extracting Entities and Relationships...")
        llm_transformer = LLMGraphTransformer(
            llm=llm,
            allowed_nodes=["Company", "Person", "Technology", "Location", "System"],
            allowed_relationships=["HEADQUARTERED_IN", "PARTNERS_WITH", "FOUNDED", "CREATED", "CEO_OF", "BUILDS", "USES", "ENHANCES"],
            strict_mode=True # <-- Forces the 8B model to strictly adhere to JSON extraction
        )
        
        # ⚡ MAGIC HAPPENS HERE: The LLM reads the English text and structures it into Graph Objects
        graph_documents = llm_transformer.convert_to_graph_documents(docs)
        
        # --- PEEK INSIDE THE LLM'S BRAIN ---
        print("\n" + "="*50)
        print("🧠 LLM SCHEMA EXTRACTION RESULTS")
        print("="*50)
        
        print("\n🟢 EXTRACTED NODES (Entities):")
        for node in graph_documents[0].nodes:
            print(f"   - [{node.type}] {node.id}")
            
        print("\n🔗 EXTRACTED RELATIONSHIPS (Edges):")
        for rel in graph_documents[0].relationships:
            print(f"   - ({rel.source.id}) -[:{rel.type}]-> ({rel.target.id})")
            
        print("\n" + "="*50 + "\n")
        # -----------------------------------

        # 4. Push the structured data directly to Neo4j
        logger.info("Connecting to Neo4j Cloud Database...")
        graph = Neo4jGraph(
            url=os.getenv("NEO4J_URI"),
            username=os.getenv("NEO4J_USER"),
            password=os.getenv("NEO4J_PASSWORD"),
            database=os.getenv("NEO4J_DATABASE", "neo4j")
        )
        
        logger.info("Injecting extracted graph schema into Neo4j via Auto-Cypher...")
        graph.add_graph_documents(graph_documents)
        
        logger.info("✅ SUCCESS! Unstructured text has been fully transformed into an Enterprise Knowledge Graph.")

    except Exception as e:
        logger.error(f"Pipeline failed: {str(e)}")