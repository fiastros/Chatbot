"""
Connects to ChromaDB and Neo4j with explicit exception handling.
"""

import chromadb
from neo4j import GraphDatabase
from neo4j.exceptions import AuthError, ServiceUnavailable
from config import settings
from logger import get_logger

logger = get_logger(__name__)

class DatabaseManager:
    def __init__(self):
        self.chroma_client = None
        self.vector_collection = None
        self.neo4j_driver = None
        self._connect_chroma()
        self._connect_neo4j()

    def _connect_chroma(self):
        try:
            self.chroma_client = chromadb.PersistentClient(path=settings.chroma_db_path)
            self.vector_collection = self.chroma_client.get_or_create_collection("document_chunks")
            logger.info("Successfully connected to ChromaDB.")
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {e}")
            raise

    def _connect_neo4j(self):
        try:
            self.neo4j_driver = GraphDatabase.driver(
                settings.neo4j_uri, 
                auth=(settings.neo4j_user, settings.neo4j_password)
            )
            self.neo4j_driver.verify_connectivity()
            logger.info("Successfully connected to Neo4j.")
        except (AuthError, ServiceUnavailable) as e:
            logger.critical(f"Neo4j Connection Failed. Check credentials or ensure Docker is running: {e}")
            raise

    def store_vectors(self, chunks: list[dict], embeddings: list[list[float]]):
        try:
            ids = [f"{c['metadata']['file_uri']}_{i}" for i, c in enumerate(chunks)]
            documents = [c['content'] for c in chunks]
            metadatas = [c['metadata'] for c in chunks]
            
            self.vector_collection.add(
                ids=ids, embeddings=embeddings, documents=documents, metadatas=metadatas
            )
            logger.info(f"Stored {len(chunks)} vectors successfully.")
        except Exception as e:
            logger.error(f"Vector storage failed: {e}")

    def store_knowledge_graph(self, entities: list[dict]):
        # Expects list of dicts: {"subject": "X", "relation": "Y", "object": "Z"}
        
        query = """
        UNWIND $entities AS entity
        MERGE (s:Node {name: entity.subject})
        MERGE (o:Node {name: entity.object})
        WITH s, o, entity
        CALL apoc.create.relationship(s, entity.relation, {}, o) YIELD rel
        RETURN count(rel)
        """
        
        try:
            with self.neo4j_driver.session() as session:
                # Using standard cypher if APOC isn't installed. Simplified for safety:
                for req in entities:
                    safe_query = f"""
                    MERGE (s:Entity {{name: $subject}})
                    MERGE (o:Entity {{name: $object}})
                    MERGE (s)-[:{req['relation'].upper().replace(' ', '_')}]->(o)
                    """
                    session.run(safe_query, subject=req['subject'], object=req['object'])
            logger.info(f"Stored {len(entities)} relationships in Neo4j.")
        except Exception as e:
            logger.error(f"Knowledge Graph insertion failed: {e}")

    def close(self):
        if self.neo4j_driver:
            self.neo4j_driver.close()