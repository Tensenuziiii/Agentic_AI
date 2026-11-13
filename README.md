# Paper-to-Presentation & Viva Agent

A Streamlit application that helps students explore a research paper, prepare a presentation, and practice viva questions. It extracts text from a PDF, retrieves page-tagged passages with ChromaDB, and sends relevant excerpts to a task-specific LangChain agent.

The assignment brief and the supplied README blueprint describe the intended scope. This README documents the implementation currently in this repository and calls out its known limitations.

## Problem this project addresses

Preparing a research presentation and anticipating examiner questions takes time. The application provides a first draft of the summary, concept explanations, presentation content, and viva practice, with paper excerpts and page references used as evidence. Generated content should be checked against the original paper.

## Current features

- Upload and index a text-based PDF; report empty, invalid, and scanned/image-only PDFs.
- Extract text per page, split into overlapping chunks, create local HuggingFace embeddings, and store chunks in a document-specific ChromaDB collection.
- Retrieve passages with page metadata and filter by document ID.
- Generate summaries and concept explanations, including a dedicated beginner-friendly/technical concept explainer.
- Generate presentation outlines and editable PowerPoint files.
- Generate viva questions, evaluate answers, and answer questions about the paper.
- Route task types to the relevant agent through a central orchestrator.
- Run the UI with a local Ollama model or configure OpenRouter as an API provider.

## Agent design

| Agent | Current responsibility |
|---|---|
| Summarizer | Produces a structured paper summary from retrieved excerpts. |
| Concept extractor | Explains requested concepts and can list important concepts, methods, contributions, and findings. |
| Slide generator | Produces a slide outline from retrieved excerpts; `python-pptx` exports it as an editable deck. |
| Viva agent | Generates questions and answers, evaluates practice answers, and handles paper Q&A. |

The orchestrator retrieves relevant passages and invokes only the agent mapped to the selected intent. The agents are specialized workflows coordinated by the application; they are not autonomous tool-using agents.

## Architecture

```mermaid
flowchart TD
  U[Streamlit UI] --> I[PDF ingestion]
  I --> P[PyMuPDF page extraction]
  P --> S[Recursive chunking]
  S --> E[HuggingFace embeddings]
  E --> C[(Document-specific ChromaDB collection)]
  U --> R[Intent selection and router]
  R --> O[Orchestrator]
  C --> O
  O --> A[Selected agent]
  A --> L[ChatPromptTemplate | Ollama or OpenRouter | StrOutputParser]
  L --> O
  O --> U
  U --> X[python-pptx export]
```

### PDF and retrieval flow

1. PyMuPDF extracts selectable text page by page and assigns one-based page metadata.
2. `RecursiveCharacterTextSplitter` creates chunks of 1,000 characters with 160 characters of overlap.
3. `sentence-transformers/all-MiniLM-L6-v2` creates local embeddings by default.
4. Chunks are stored in ChromaDB under a collection derived from the PDF SHA-256 hash. Retrieval also filters by that document ID.
5. The orchestrator passes retrieved text and page references to the selected agent.

Scanned PDFs without selectable text need OCR before upload; OCR is not included.

### Intent routing and LCEL

Supported intents are `SUMMARY`, `CONCEPT_EXTRACTION`, `SLIDE_GENERATION`, `VIVA_GENERATION`, `VIVA_PRACTICE`, and `PAPER_QA`. `core/router.py` provides keyword-based intent detection. The UI also lets users choose tasks directly. The orchestrator dispatches to one agent rather than invoking all agents.

`core/llm.py` composes LangChain chains using `ChatPromptTemplate | ChatOllama/ChatOpenAI | StrOutputParser`. The system prompt asks the model to ground claims in supplied excerpts, cite page metadata, and state when the excerpts do not support an answer. A Pydantic model validates that the returned text is non-empty; structured JSON output validation is not currently implemented.

## Technology stack

| Layer | Technology |
|---|---|
| Interface | Streamlit and custom CSS |
| Backend | Python 3.10+ |
| Local LLM | Ollama through `langchain-ollama` |
| API LLM option | OpenRouter's OpenAI-compatible API through `langchain-openai` |
| Prompt/workflow | LangChain prompt templates, LCEL, and output parsers |
| PDF extraction | PyMuPDF |
| Text splitting | LangChain `RecursiveCharacterTextSplitter` |
| Embeddings | HuggingFace Sentence Transformers |
| Vector database | ChromaDB |
| Slides | `python-pptx` |
| Validation | Pydantic |

## Project structure

```text
app.py                 Streamlit entry point
agents/                Summarizer, concept, slide, and viva agents
core/                  LLM provider, schemas, intent router, orchestrator
ingestion/             PDF extraction, chunking, and retrieval
services/              PowerPoint generation
ui/                    Streamlit styling
tests/                 Routing, extraction, orchestration, and PPTX checks
requirements.txt       Python dependencies
.env.example           Safe configuration template
.gitignore             Excludes secrets and local data
```

## Installation and setup

Python 3.10 or newer is recommended. Run commands from the project directory.

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `.env` to select an LLM provider, then run the app:

```powershell
streamlit run app.py
```

### Use Ollama (local model)

Install Ollama separately, then run:

```powershell
ollama pull llama3.2
ollama serve
```

Set `LLM_PROVIDER=ollama` and adjust `OLLAMA_MODEL` or `OLLAMA_BASE_URL` in `.env` if needed. Ollama generation stays on the local machine.

### Use OpenRouter

Set these values in `.env`:

```dotenv
LLM_PROVIDER=openrouter
OPENROUTER_API_KEY=your_key_here
OPENROUTER_MODEL=openrouter/free
```

OpenRouter requests go to a hosted model provider; paper excerpts included in prompts are sent outside the computer. Free models may have rate limits or temporary availability issues. Never commit `.env` or put an API key in source code. Use `.env.example` as the shareable template.

### Other configuration

```dotenv
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
CHROMA_DIR=./.chroma
```

The embedding model downloads on first use, so initial setup requires internet access. Later embedding and retrieval run locally by default.

## Run tests

```powershell
python -m pytest -q
```

The current tests cover intent routing, invalid and empty PDFs, page extraction and chunk metadata, selected-agent orchestration with a mocked agent, and PPTX container creation. They do not make live LLM calls or test a full ChromaDB/HuggingFace ingestion cycle.

## Assignment acceptance criteria

| Criterion | Implementation in this project |
|---|---|
| LLM integration | Ollama local model or configured OpenRouter provider. |
| Interactive GUI | Streamlit upload, tabs, chat, practice controls, and downloads. |
| Prompt engineering | Grounding, citation, uncertainty, and agent-specific task prompts. |
| Prompt templates and LCEL | `core/llm.py` builds prompt/model/parser sequences. |
| Agentic RAG | Page extraction, chunking, embeddings, ChromaDB retrieval, metadata, and orchestration. |
| Intent detection and routing | `core/router.py`, typed intent schema, and orchestrator dispatch. |
| ChromaDB | Persistent per-document collections and document-ID filters. |

## Known limitations

- OCR for scanned PDFs is not included.
- LLM behavior depends on the selected provider, model access, connectivity, and quotas. The application cannot guarantee that a free API model will be available for every request.
- The system uses retrieved excerpts and prompts to request citations; it does not independently verify every generated citation against the entire paper.
- LLM output validation currently checks for non-empty text, not a structured response schema.
- PDF file-size limits, automatic title/bibliography extraction, slide speaker notes, and export of viva reports are not implemented.
- Viva progress is kept in Streamlit session state and is lost when that session ends.

## Academic note

This is a study and presentation assistant, not a substitute for reading the research paper. Check generated summaries, slide claims, citations, and suggested viva answers against the source before using them in academic work.
