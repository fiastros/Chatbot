## Frameworks and Tools
- [Frameworks and Tools](#frameworks-and-tools)
- [Phase 1: Data Ingestion Pipeline (Offline)](#phase-1-data-ingestion-pipeline-offline)
- [Phase 2: Runtime Initiation \& Orchestration](#phase-2-runtime-initiation--orchestration)
- [Phase 3: Agentic Execution \& Tool Calling](#phase-3-agentic-execution--tool-calling)
- [Phase 4: The RAG Pipeline Tool (Retrieval \& Search)](#phase-4-the-rag-pipeline-tool-retrieval--search)
- [Phase 5: Context Augmentation](#phase-5-context-augmentation)
- [Phase 6: Validation, Synthesis \& Output](#phase-6-validation-synthesis--output)
- [Phase 7: LLMOps, Security \& Observability](#phase-7-llmops-security--observability)


## Phase 1: Data Ingestion Pipeline (Offline)
*This happens entirely in the background before a user ever interacts with the system. Its goal is to prepare and strictly organize raw data.*

| Component | Main Choice | Pros & Cons (Tailored for M1 / 30GB SSD limits) | Alternatives (By Popularity) |
| :--- | :--- | :--- | :--- |
| **Document Parser** | `docling` [Local] | Extracts and parses PDFs, Word docs, and images directly into hyper-clean Markdown, which is highly token-efficient for LLM processing. | `Unstructured`, `PyMuPDF`, `LlamaParse` (Cloud API), `MarkItDown` (Microsoft), `Tika` |
| **Vector Database** | `chromadb` [Local] | Stores multimodal embeddings for semantic similarity searches. It runs completely locally as a serverless file inside your Python environment. | `Redis`, `Qdrant`, `Milvus Lite`, `Faiss`, `Weaviate`, `LanceDB` |
| **Graph Database** | `Neo4j AuraDB` [Cloud] | Extracts entities and relationships to build a Knowledge Graph (prep for Graph-RAG). Free cloud tier protects local SSD. | `Neo4j Desktop`, `Kùzu`, `Memgraph`, `NebulaGraph` |
| **Object Store** | `sqlite3` [Local] | Stores the untouched, original raw files so they can be retrieved as citations later. Built natively into Python, requiring zero extra installation or background servers. | `PostgreSQL`, `MongoDB` (Local), `DuckDB`, `TinyDB` |
| **Embeddings** | `sentence-transformers` & `torch` [Local] | Generates the mathematical vector embeddings for text and images. Uses Apple Metal Performance Shaders (MPS) to utilize the M1 GPU. | `HuggingFace Embeddings`, `nomic-embed-text` (via Ollama), `FastEmbed`, `Jina Embeddings` |


## Phase 2: Runtime Initiation & Orchestration
*The moment the user submits a prompt, the system intercepts it, checks for safety, and builds a plan.*

| Component | Main Choice | Pros & Cons (Tailored for M1 / 16GB RAM limits) | Alternatives (By Popularity) |
| :--- | :--- | :--- | :--- |
| **Semantic Caching** | `gptcache` [Local] | Checks if the exact question has been asked recently and serves the cached answer instantly, bypassing the entire pipeline. | `langchain-cache`, `Redis Semantic Cache` |
| **Orchestrator** | `langgraph` [Local] | Determines the workflow/execution pattern and delegates tasks. It creates cyclic, state-machine workflows. | `CrewAI`, `AutoGen`, `Semantic Kernel`, `Phidata`, `IBM BeeAI` |
| **Local SLM Engine** | `Ollama` & `LM Studio` [Local] | Uses `llama.cpp` under the hood to run heavily quantized models natively on Apple Silicon. LM Studio provides a visual UI to strictly monitor and delete massive model files. | `llama.cpp` (Raw CLI), `vLLM`, `GPT4All`, `MLX` (Apple Native) |
| **Core SLM** | `Phi-3-Mini` (4k, 4-bit) [Local] | Highly capable at logic while consuming only ~2.5GB of RAM, leaving vital system memory free for embeddings and workflow state. | `Llama-3-8B-Instruct`, `Qwen-2.5-3B`, `Gemma-2-2B`, `IBM-Granite Models` |
| **Vision Model** | `Moondream2` [Local] | Ultra-tiny 1.8B parameter model; provides fast vision analysis without stalling the M1 chip. | `LLaVA-1.5` (7B), `Qwen-VL`, `Phi-3-Vision` |
| **Cloud API Logic** | `Groq API` [Cloud] | Generous free tier utilizing custom LPUs for massive generation speed (Commercial use allowed). | `Google Gemini API` (Free Tier), `Cohere API` (Free Tier), `Together AI` |


## Phase 3: Agentic Execution & Tool Calling
*The system delegates the plan to specialized workers who decide which tools to use.*

| Component | Main Choice | Pros & Cons (Tailored for Free Commercial Tiers) | Alternatives (By Popularity) |
| :--- | :--- | :--- | :--- |
| **Agent Framework** | `langchain` & `langchain-core` [Local] | Foundational wrappers that give agents access to external tools and ReAct/CoT reasoning templates. | `LlamaIndex`, `Haystack`, `SmolAgents` |
| **Web Search Tool** | `DuckDuckGoSearchRun` [Local] | Scrapes DuckDuckGo for live news and web data when the agent decides it needs to search the web. 100% free and requires no API keys. | `Tavily`, `Google Custom Search API`, `Serper API`, `SearxNG` |


## Phase 4: The RAG Pipeline Tool (Retrieval & Search)
*Triggered ONLY if the Researcher Agent decides it needs internal company knowledge.*

| Component | Main Choice | Pros & Cons (Tailored for M1 / Low Latency) | Alternatives (By Popularity) |
| :--- | :--- | :--- | :--- |
| **Routing Agent** | `semantic-router` [Local] | Lightweight classifier that looks at the specific sub-query and routes it to the most efficient database. Bypasses expensive LLM calls entirely. | `LLM-based Conditional Routing`, `Zero-Shot Classifiers` |
| **Reranking** | `flashrank` [Local] | Strictly re-orders newly retrieved chunks based on absolute relevance. Ultra-lightweight and runs optimally on CPU/Apple Silicon. | `Cohere Rerank API`, `BGE-Reranker`, `Heavy PyTorch Cross-Encoders` |


## Phase 5: Context Augmentation
*Formatting and cleaning the retrieved data before the LLM is allowed to read it.*

| Component | Main Choice | Pros & Cons (Tailored for Interoperability & Safety) | Alternatives (By Popularity) |
| :--- | :--- | :--- | :--- |
| **Data Masking** | `presidio-analyzer` & `presidio-anonymizer` [Local] | Strips sensitive PII from the text before it enters the prompt. Microsoft's open-source library runs completely locally. | `Google DLP API` (Cloud), `Custom Regex Patterns`, `Scrubadub` |
| **Prompt Engineering** | `LangChain Prompts` [Local] | Native integration directly into your orchestrator. Requires zero overhead to hook into LangGraph state variables or local SLM execution. | `DSPy`, `Promptfoo`, `Hardcoded Strings` |


## Phase 6: Validation, Synthesis & Output
*Generating the final answer, checking it for errors, and presenting it safely.*

| Component | Main Choice | Pros & Cons (Tailored for Stability) | Alternatives (By Popularity) |
| :--- | :--- | :--- | :--- |
| **Structured Output** | `pydantic` [Local] | Forces the final generated answer into strict, validated JSON schemas so downstream UI systems don't break. | `JSON Schema`, `Marshmallow`, `TypeDict` |
| **Synthesis** | `instructor` [Local] | Patches the LLM APIs to guarantee they output the strict Pydantic JSON objects requested. Plugs natively into LangChain setups. | `Outlines`, `Guidance`, `Marvin` |
| **Output Guardrails** | `nemoguardrails` [Local] | Checks the output to ensure it contains no hallucinations or toxic content. Offers flexible, programmable routing beyond just toxicity. | `Llama-Guard`, `Guardrails AI`, `Aporia` |


## Phase 7: LLMOps, Security & Observability
*The overarching layer that monitors health, speed, and accuracy.*

| Component | Main Choice | Pros & Cons (Tailored for 30GB SSD limits) | Alternatives (By Popularity) |
| :--- | :--- | :--- | :--- |
| **Tracing & Telemetry** | `langsmith` [Cloud] | Visualizes step-by-step agent thoughts and logs latency metrics. Utilizes the cloud tier to keep heavy logging data off the local machine. | `Langfuse`, `Phoenix by Arize`, `Helicone`, `Kibana / ELK Stack` |
| **Evaluation Framework** | `ragas` [Local Engine / Cloud LLM] | Automates quality assurance by having a stronger model grade the system's outputs over time based on Context Precision, Answer Relevance, and Faithfulness. | `TruLens`, `DeepEval`, `Arize AI` |