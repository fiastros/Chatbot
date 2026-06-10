"""
Entry point for the Agentic Ingestion Pipeline.
Initializes the agent, processes a target file, and handles exceptions gracefully.
"""

from logger import get_logger
from databases import DatabaseManager
from agent import IngestionAgent

logger = get_logger("main")

def main():
    logger.info("Initializing Agentic Ingestion Pipeline...")
    
    try:
        db_manager = DatabaseManager()
        agent = IngestionAgent(db_manager)
        
        target_file = "/Users/fiastros/Documents/personnal_projects/Fatala/chatbot/documents/SVEPM-book.pdf"
        agent.process_file(target_file)
        
    except Exception as e:
        logger.critical(f"Pipeline crashed: {e}")
    finally:
        if 'db_manager' in locals():
            db_manager.close()
            logger.info("Database connections closed.")

if __name__ == "__main__":
    main()