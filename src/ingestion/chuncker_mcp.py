"""
There isn't a single pre-packaged "LlamaIndex Chunker" executable on PyPI yet, 
as LlamaIndex MCPs are usually built custom per project. However, since we are using uv,
we can quickly create a micro-server file in your project and run it.
"""

import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from llama_index.core.node_parser import SemanticSplitterNodeParser
from llama_index.embeddings.ollama import OllamaEmbedding

app = FastAPI()
embed_model = OllamaEmbedding(model_name="all-minilm")
splitter = SemanticSplitterNodeParser(buffer_size=1, breakpoint_percentile_threshold=95, embed_model=embed_model)

class ChunkRequest(BaseModel):
    text: str
    file_uri: str

@app.post("/sse") # Mocking the SSE endpoint for the agent
async def chunk_text(request: ChunkRequest):
    nodes = splitter.get_nodes_from_documents([request.text])
    chunks = [{"content": node.text, "metadata": {"file_uri": request.file_uri}} for node in nodes]
    return {"chunks": chunks}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)