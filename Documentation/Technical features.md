# Technical specs & features of the App

## Table of Contents
- [Technical specs \& features of the App](#technical-specs--features-of-the-app)
  - [Table of Contents](#table-of-contents)
  - [Architecture Flow Chart](#architecture-flow-chart)
  - [Phase 1: Data Ingestion Pipeline (Offline)](#phase-1-data-ingestion-pipeline-offline)
  - [Phase 2: Runtime Initiation \& Orchestration](#phase-2-runtime-initiation--orchestration)
  - [Phase 3: Agentic Execution \& Tool Calling](#phase-3-agentic-execution--tool-calling)
  - [Phase 4: The RAG Pipeline Tool (Retrieval \& Search)](#phase-4-the-rag-pipeline-tool-retrieval--search)
  - [Phase 5: Context Augmentation](#phase-5-context-augmentation)
  - [Phase 6: Validation, Synthesis \& Output](#phase-6-validation-synthesis--output)
  - [Phase 7: LLMOps, Security \& Observability](#phase-7-llmops-security--observability)


##  Architecture Flow Chart

<img src="multi-agent-architecture.svg" alt="multi-agent-architecture" />


## Phase 1: Data Ingestion Pipeline (Offline)
*This happens entirely in the background before a user ever interacts with the system. Its goal is to prepare and strictly organize raw data.*

* **Document Parser Agent:** Scans raw files (PDFs, Excels, Word docs, Images) using specific tools like OCR or Table Extractors.
    * *Example:* If it receives a scanned invoice, it uses OCR; if it receives an Excel file, it triggers a tabular data parser.
* **Semantic & Hierarchical Chunking:** Breaks documents apart by meaning (paragraphs) rather than arbitrary character counts, while maintaining parent/child relationships (e.g., a page summary linking to specific paragraphs). 
    * *Example:* Keeping a full legal clause together in one chunk so the context isn't sliced in half.
* **Sliding Windows:** Overlaps text chunks slightly to prevent important sentences from being cut off at boundaries.
* **Deduplication & Metadata Enrichment:** Identifies and extracts dates, entities, and domain tags. Crucially, it attaches **File URIs** (pointers to the original files) to every chunk.
* **Parallel Processing & Database Storage:** The processed chunks are split into three separate databases for different purposes:
    * **Vector Database:** Stores multimodal embeddings (text, images, charts mapped to a shared Euclidean space via CLIP) for similarity search.
    * **Graph Database:** Extracts entities and relationships to build a Knowledge Graph (prep for Graph-RAG).
    * **Object Store (Blob DB):** Stores the untouched, original raw files so they can be retrieved as citations later.


## Phase 2: Runtime Initiation & Orchestration

*The moment the user submits a prompt, the system intercepts it, checks for safety, and builds a plan.*

* **Input Guardrails:** Intercepts the query to block prompt injections or malicious inputs.
* **Vector / Semantic Caching:** Checks if this exact question has been asked recently. If yes, it serves the cached answer instantly, bypassing the entire pipeline.
    * *Example:* Hundreds of employees asking "What is the company holiday schedule?" on the same day will only trigger a full search once.
* **Orchestrator Agent (The Manager):** Determines the workflow/execution pattern (e.g., Plan-and-Execute). It analyzes the user's intent, breaks complex queries into sub-tasks, and delegates them.
    * *Example:* User asks, "What were our Q3 margins and how do they compare to industry averages?" The Orchestrator splits this into two tasks: 1) Find internal Q3 margins, 2) Search the web for industry averages.



## Phase 3: Agentic Execution & Tool Calling
*The system delegates the plan to specialized workers who decide which tools to use.*

* **Researcher Agent:** Uses Reasoning/Planning/Acting (ReAct/CoT) to execute the Orchestrator's plan.
* **Tool Calling:** The agent decides *if* it needs to search a database, do math, or search the web.
    * *Decision 1:* If calculating a percentage, it uses the **Calculator Tool**.
    * *Decision 2:* If needing live news, it uses the **Web Search Tool**.
    * *Decision 3:* If needing company data, it triggers the **Internal RAG Pipeline Tool**.


## Phase 4: The RAG Pipeline Tool (Retrieval & Search)
*Triggered ONLY if the Researcher Agent decides it needs internal company knowledge.*

* **Semantic Routing Agent:** A lightweight classifier that looks at the specific sub-query and routes it to the most efficient database.
    * *Query: "Who manages John Doe?" -> Router sends to Graph DB (best for relationships).*
    * *Query: "What is the vacation policy?" -> Router sends to Vector DB (best for document text).*
    * *Query: "Hello, how are you?" -> Router bypasses databases entirely and just answers.*
    * *Why it's useful:* Saves massive amounts of latency and compute costs by avoiding expensive vector searches for simple or irrelevant queries.
* **Query Transformation:** Uses techniques like HyDE or step-back prompting to translate the user's casual phrasing into optimal search terms.
* **Hybrid Search:** Fetches the initial data using a combination of dense vector search (semantic meaning) and sparse search (exact keyword matching).
* **Cross-encoder Reranking:** Strictly re-orders the newly retrieved chunks based on absolute relevance.
* **Contextual Compression:** Extracts only the highly relevant sentences from those reranked chunks, reducing noise and API token costs.


## Phase 5: Context Augmentation
*Formatting and cleaning the retrieved data before the LLM is allowed to read it.*

* **Redaction / Data Masking:** Strips sensitive PII (like Social Security Numbers) from the text before it enters the prompt.
* **Dynamic Few-Shot Prompting:** Automatically injects the most relevant historical Q&A examples to show the LLM how to format its answer.
* **Context Window Management:** Tracks tokens to ensure the injected data doesn't exceed the LLM's memory limits, preventing crashes.
* **Prompt Optimization:** Uses algorithmic frameworks (like DSPy) to compile and optimize the final prompt under the hood.


## Phase 6: Validation, Synthesis & Output
*Generating the final answer, checking it for errors, and presenting it safely.*

* **Critic & Validator Agent:** Reviews the Researcher's gathered data using self-correction loops.
    * *Example:* If the Researcher pulled Q2 data but the user asked for Q3, the Critic rejects it and sends the Researcher back to search again.
* **Human-in-the-Loop (HITL):** Pauses the workflow to require human approval before executing any high-stakes actions.
    * *Example:* The agent drafts an email to a client, but waits for you to click "Approve" before actually sending it.
* **Synthesizer Agent:** Takes the validated data and constructs the final response. It uses the File URIs attached to the data chunks to fetch the original documents from the Blob DB, creating clickable citations.
* **Structured Output Constraints:** Forces the final generated answer into strict, validated JSON schemas so downstream UI systems don't break.
* **Output Guardrails:** A final dedicated model checks the output to ensure it contains no hallucinations or toxic content before showing it to the user.


## Phase 7: LLMOps, Security & Observability
*The overarching layer that monitors health, speed, and accuracy.*

* **Tracing & Telemetry:** Visualizes step-by-step agent thoughts and logs latency metrics across the generation and augmentation pipelines.
* **Evaluation Frameworks (LLM-as-a-judge):** Automates quality assurance by having a stronger model grade the system's outputs over time based on Context Precision, Answer Relevance, and Faithfulness.
* **Shadow Testing:** Routes a percentage of live traffic to new experimental prompts or models in the background. 
    * *Example:* Testing a new prompt update secretly; the user sees the normal system's answer, while the developers compare it to the experimental system's answer to ensure the update works before a full rollout.

