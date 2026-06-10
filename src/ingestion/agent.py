"""
This sets up llama3.1 via LlamaIndex, connects to the MCP servers, and establishes the advanced system prompt for the workflow.
"""

# src/ingestion/agent.py
import json
from llama_index.core.agent import ReActAgent
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.core.tools import FunctionTool
# Assuming you are using an HTTP/REST wrapper for the external MCP servers
import requests 

from config import settings
from logger import get_logger
from databases import DatabaseManager

import asyncio
import json

logger = get_logger(__name__)

# --- Dummy Wrappers for External MCP SSE Endpoints ---
# In a true setup, you might use LlamaIndex's MCPToolSpec.
# Here we define Python functions that call your separate terminal servers.
def call_docling_mcp(file_path: str) -> str:
    """Sends a file path to the external Docling MCP server to parse it to Markdown."""
    logger.info(f"Agent calling Docling MCP for {file_path}")
    # Example REST call to your SSE/HTTP MCP server
    response = requests.post(settings.docling_mcp_url, json={"file": file_path})
    return response.json().get("markdown")
    # return f"# Parsed Content of {file_path}\n\nThis is the extracted text."

def call_chunker_mcp(markdown_text: str, strategy: str = "semantic") -> list[dict]:
    """Sends markdown to the LlamaIndex Chunker MCP. Strategy can be 'semantic' or 'sliding_window'."""
    logger.info(f"Agent calling Chunker MCP using {strategy} strategy")
    response = requests.post(settings.chunker_mcp_url, json={"text": markdown_text, "strategy": strategy})
    return response.json().get("chunks")
    # return [{"content": markdown_text, "metadata": {"file_uri": "test.pdf"}}]

class IngestionAgent:
    def __init__(self, db_manager: DatabaseManager):
            self.db = db_manager
            
            # Initialize Llama 3.1
            self.llm = Ollama(model="ollama3.1", request_timeout=120.0)
            
            # Initialize Embedder (Using Ollama to host all-minilm natively)
            self.embedder = OllamaEmbedding(model_name="all-minilm") # all-minilm nomic-embed-text
            
            self.tools = [
                FunctionTool.from_defaults(fn=call_docling_mcp),
                FunctionTool.from_defaults(fn=call_chunker_mcp),
            ]
            
            self.system_prompt = """
            You are an advanced Data Ingestion Architect Agent. 
            Your goal is to process raw files into a structured database system.
            
            Workflow Instructions:
            1. Parse the document using the 'call_docling_mcp' tool.
            2. Analyze the language of the parsed text. If it is NOT in English, translate the core concepts into English in your mind before proceeding.
            3. Determine the best chunking strategy (e.g., 'semantic' for markdown docs, 'sliding_window' for raw text) and use the 'call_chunker_mcp' tool.
            4. Analyze the text and extract key Knowledge Graph entities. Format them STRICTLY as a JSON array of objects with "subject", "relation", and "object" keys. Do NOT output markdown JSON blocks, just the raw JSON array string.
            """
            
            self.agent = ReActAgent(
                tools=self.tools, 
                llm=self.llm, 
                verbose=True, 
                system_prompt=self.system_prompt
            )

    def process_file(self, file_path: str):
            logger.info(f"Starting agentic ingestion for: {file_path}")
            
            prompt = f"Process the file at '{file_path}'. Extract the knowledge graph relationships as a strict JSON string."
            
            # Wrap the workflow execution in an async function so we can properly 'await' the handler
            async def _run_agent():
                # Workflows require the prompt to be passed as 'user_msg'
                return await self.agent.run(user_msg=prompt)
                
            try:
                # Safely execute the async workflow inside the synchronous Python script
                result = asyncio.run(_run_agent())
                
                # Extract the response safely depending on the Workflow's return structure
                if hasattr(result, "response"):
                    raw_json = str(result.response).strip()
                elif isinstance(result, dict) and "response" in result:
                    raw_json = str(result["response"]).strip()
                else:
                    raw_json = str(result).strip()
                    
                # Clean up markdown formatting if the LLM wrapped the JSON
                if raw_json.startswith("```json"):
                    raw_json = raw_json[7:-3].strip()
                elif raw_json.startswith("```"):
                    raw_json = raw_json[3:-3].strip()
                    
                kg_entities = json.loads(raw_json)
                self.db.store_knowledge_graph(kg_entities)
                
                logger.info("Agent successfully completed ingestion workflow.")
                
            except json.JSONDecodeError:
                logger.error(f"Agent failed to output valid JSON for the Knowledge Graph. Raw output: {raw_json}")
            except Exception as e:
                logger.error(f"Agent execution failed: {e}")