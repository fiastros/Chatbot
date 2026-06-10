uv pip install llama-index llama-index-llms-ollama llama-index-embeddings-ollama mcp neo4j chromadb pydantic-settings docling sentence-transformers torch fastapi uvicorn 

ollama serve
ollama run llama3.1

docker-compose up -d

uvx --from=docling-mcp docling-mcp-server --transport sse --port 8001
uv run chunker_mcp.py


## Minimum hardware specs (my local setup)

- OS: Macbook air 13''
- RAM: 16 gb
- SSD: 30 GB
- CPU: 8 cores (4 performance and 4 efficiency)
- Chip: Apple M1

### Compute Memory  needed to run an LLM

This will give you the total space needed for your LLM: </br>
To determine if a model will load, you must sum three components Model Weights (number of parameters * Bytes per parameters) +  KV Cache memory (2 * layers * hidden dim * context length * 2 bytes), and System/App Overhead (os, browser and IDE and extra). </br>
 TOTAL : model weights memory + KV cache memory + OS memory

### Compute Speed of an LLM on your machine

For speed calculation: </br>
memory-bandwidth bound (60 or 70 GB/s on M1) meaning how can M1 chip can move data from RAM to GPU cores</br>
 Formula = memory beandwidth / model size


<details>
<summary> ToDo </summary>



- [ ] link the main readme to the technical docs: technical specs
- [x] write my hardware specs I used to run the project ?
- [ ] Create the technical docs of libraries/languages used
- [ ] the current architecture doesn't handle different language, badwords ...
- [ ] How to estimate power consumption of an LLM model
- [ ] How to estimate hardware requirements of an LLM/SLM etc ... (training and inference time)
- [ ] Improve the technical feature description of the project
- [ ] In the technical specs i need the user to be able to loads his own documents (all sorts of documents) for question answering and other things
- [ ] long term-memory handling
- [ ] I need organize my repository with folders, subfolders, files, ... 
    #### Project Metadata & Governance
- [ ] CHANGELOG.md: A chronological list of versions and what changed in each.
- [ ] CONTRIBUTING.md: Guidelines for how others should submit code, report bugs, or request features.
    #### Configuration & Development Environment

- [ ] .editorconfig: Forces consistent indentation and spacing across different code editors (VS Code, IntelliJ, etc.).
- [ ] .env.example: A template file showing which environment variables the app needs (e.g., API_KEY=your_key_here) without including your real secrets.
- [ ] .pre-commit-config.yaml: Automates tasks (like linting or formatting) before a commit is even allowed, ensuring only "clean" code enters your history.
    #### CI/CD & Automation
- [ ] .github/workflows/: This directory contains YAML files for GitHub Actions. These files define your CI/CD pipelines—for example, automatically running your make test command every time someone opens a Pull Request.
- [ ] Dockerfile / docker-compose.yml: Define how to containerize your application. This makes your code "run anywhere," which is a hallmark of production-readiness

    #### CI/CD & Automation
- [ ] docs/: A folder for more in-depth architectural diagrams, API documentation, or developer guides that don't fit well in the main README.
- [ ] 