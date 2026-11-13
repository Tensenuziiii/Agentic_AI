# Paper-to-Presentation & Viva Agent

A local-first academic assistant that indexes a research-paper PDF and uses specialized agents to produce grounded summaries, concept explanations, editable presentations, viva preparation, answer feedback, and paper Q&A.

## Features

- Page-aware PDF extraction with selectable-text validation and helpful scanned-PDF errors.
- Overlapping recursive chunks, local Sentence Transformers embeddings, document-specific Chroma collections, and metadata-filtered retrieval.
- Six-way intent routing and a central orchestrator that invokes only the requested agent.
- Four agents: summarizer, concept extractor, slide generator, and viva agent.
- Ollama chat model (default `llama3.2`) through LangChain prompt templates and LCEL.
- Editable PPTX generation; basic, intermediate, and advanced viva questions; interactive response evaluation.
- Streamlit GUI with paper status, chat, download, and session state.
- No hosted model API or paid key required. The embedding model is downloaded on first use; uploaded paper content and the Chroma index remain local by default.

## Architecture

```mermaid
flowchart TD
  U[Streamlit UI] --> R[Intent router]
  U --> I[PDF ingestion]
  I --> P[PyMuPDF page extraction]
  P --> S[Recursive chunking]
  S --> E[Local HuggingFace embeddings]
  E --> C[(ChromaDB: document collection)]
  R --> O[Orchestrator]
  O -->|relevant excerpts + request| A{Relevant agent}
  C --> O
  A --> L[LCEL prompt | Ollama | parser]
  L --> O
  O --> U
  U --> X[python-pptx export]
```

## Agent responsibilities

| Agent | Responsibility |
|---|---|
| Summarizer | Overview, problem, objectives, methodology, results, limitations, and conclusion. |
| Concept extractor | Contributions, algorithms, methods, technologies, and beginner/technical explanations. |
| Slide generator | Presentation outline grounded in retrieved paper excerpts; exported as an editable PPTX. |
| Viva agent | Questions and model answers, paper Q&A, and scored practice feedback with missing points. |

## Technology and structure

Python, Streamlit, Ollama, LangChain + LCEL, PyMuPDF, Sentence Transformers, ChromaDB, Pydantic, and python-pptx.

```text
app.py
agents/          specialized agent classes
core/            LCEL model chain, schemas, router, orchestrator
ingestion/       page extraction, chunking, embedding, retrieval
services/        presentation export
ui/              Streamlit styling
tests/           routing, PDF error, and PPTX checks
```

## Installation and running

Python 3.10 or newer is recommended.

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
ollama pull llama3.2
ollama serve
```

In another terminal, from this directory:

```powershell
streamlit run app.py
```

Configure `OLLAMA_MODEL`, `OLLAMA_BASE_URL`, `EMBEDDING_MODEL`, and `CHROMA_DIR` in `.env` as needed. Default model is `llama3.2`; Ollama must be running locally. The first embedding run downloads the configured HuggingFace model. For scanned PDFs, run OCR externally and upload a text-searchable PDF.

To use OpenRouter instead, set `LLM_PROVIDER=openrouter`, put your key in `OPENROUTER_API_KEY` in `.env`, and choose a model with `OPENROUTER_MODEL` (default `openrouter/free`). OpenRouter uses its OpenAI-compatible API endpoint; requests leave the machine to reach the selected provider. Never commit `.env` or paste API keys into source files.

## RAG and LCEL

PyMuPDF extracts each page and its one-based page number. `RecursiveCharacterTextSplitter` creates 1,000-character chunks with 160-character overlap. HuggingFace embeddings are stored in a Chroma collection whose name is derived from the uploaded PDF's SHA-256; every query also filters on that document ID. Retrieved page-tagged excerpts are passed to the single agent selected by the orchestrator. Agents use `ChatPromptTemplate | ChatOllama | StrOutputParser` LCEL chains. Prompts require the model to state when the supplied excerpts do not establish an answer and to cite excerpt page metadata.

`core.router.detect_intent` maps requests to SUMMARY, CONCEPT_EXTRACTION, SLIDE_GENERATION, VIVA_GENERATION, VIVA_PRACTICE, or PAPER_QA. Main UI controls select the corresponding specialist explicitly; free-form paper Q&A uses the paper-QA route.

## Tests

```powershell
pytest -q
```

The tests cover deterministic routing, invalid/empty PDF handling, and generation of a valid PPTX container. A full interactive run also requires a working Ollama service and the embedding model.

## Assignment acceptance criteria

| Criterion | Implementation |
|---|---|
| LLM integration | Local Ollama via `langchain-ollama`. |
| Interactive GUI | Streamlit upload, tabs, chat, practice controls, and download. |
| Prompt engineering | Grounding, citation, uncertainty, and task-specific agent instructions. |
| Prompt templates + LCEL | `core/llm.py` constructs `prompt | llm | parser`. |
| Agentic RAG | PDF page extraction, splitting, local embeddings, retrieval, metadata, and agent context. |
| Intent detection/routing | `core/router.py`, typed request schema, and orchestrator dispatch. |
| ChromaDB | Per-document collection and document-ID retrieval filter. |

## Privacy and limitations

PDFs are processed locally by default. Ollama and the HuggingFace embedding model need local disk and memory; the first model download requires network access. OCR is not bundled. Model responses can still be imperfect, so verify citations against the paper. The viva session stores scores and answers in Streamlit session state and resets when the session is lost.
