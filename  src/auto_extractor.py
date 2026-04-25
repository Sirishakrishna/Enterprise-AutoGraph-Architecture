import os
import logging
from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_groq import ChatGroq
from langchain_experimental.graph_transformers import LLMGraphTransformer
from langchain_neo4j import Neo4jGraph

# Load hidden keys
load_dotenv()

# Configure enterprise logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info("Starting Enterprise Auto-Graph Extraction Pipeline...")

    # 1. Unstructured Data (Simulating a complex enterprise document)
    unstructured_text = """
    Databricks is a data and AI company founded by Matei Zaharia. 
    Databricks created Apache Spark and MLflow. 
    Visa is a global payments technology company headquartered in San Francisco. 
    Ryan McInerney is the CEO of Visa. 
    Visa uses Databricks to build Data Intelligence Platforms for fraud detection.
    """
    
    docs = [Document(page_content=unstructured_text)]
    logger.info("Unstructured document loaded into memory.")

    try:
        # 2. Initialize the LLM (70B model is required for complex JSON schema extraction)
        logger.info("Initializing Llama-3.1 (70B) for extraction...")
        llm = ChatGroq(
            groq_api_key=os.getenv("GROQ_API_KEY"),
            model_name="llama-3.1-70b-versatile", 
            temperature=0
        )

        # 3. Initialize the Graph Transformer
        logger.info("Extracting Entities and Relationships using LLMGraphTransformer...")
        llm_transformer = LLMGraphTransformer(llm=llm)
        
        # ⚡ MAGIC HAPPENS HERE: LLM parses text into graph structures
        graph_documents = llm_transformer.convert_to_graph_documents(docs)
        
        extracted_nodes = len(graph_documents[0].nodes)
        extracted_edges = len(graph_documents[0].relationships)
        logger.info(f"Extraction Complete! Found {extracted_nodes} Nodes and {extracted_edges} Relationships.")

        # 4. Push directly to Neo4j
        logger.info("Connecting to Neo4j Cloud Database...")
        graph = Neo4jGraph(
            url=os.getenv("NEO4J_URI"),
            username=os.getenv("NEO4J_USER"),
            password=os.getenv("NEO4J_PASSWORD"),
            database=os.getenv("NEO4J_DATABASE", "neo4j")
        )
        
        logger.info("Injecting extracted graph into Neo4j...")
        graph.add_graph_documents(graph_documents)
        
        logger.info("✅ SUCCESS! Unstructured text has been fully transformed into an Enterprise Knowledge Graph.")

    except Exception as e:
        logger.error(f"Pipeline failed: {str(e)}")