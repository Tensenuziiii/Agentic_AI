import pytest
import fitz
from core.router import detect_intent
from core.schemas import Intent, Paper
from core.orchestrator import PaperOrchestrator
from ingestion.pipeline import extract_pages, chunk_pages
from services.presentation import make_presentation

def test_intent_routing():
    assert detect_intent("make slides for this paper") == Intent.SLIDE_GENERATION
    assert detect_intent("what does the paper say about data") == Intent.PAPER_QA

def test_invalid_and_empty_pdf_errors():
    with pytest.raises(ValueError): extract_pages(b"")
    with pytest.raises(ValueError): extract_pages(b"not a pdf")

def test_pptx_generation():
    payload = make_presentation("Paper", "## Slide 1: Intro\n- Finding [p. 1]")
    assert payload[:2] == b"PK"

def test_page_extraction_and_chunk_metadata():
    pdf = fitz.open()
    page = pdf.new_page()
    page.insert_text((72, 72), "A grounded paper passage about a research method.")
    docs = extract_pages(pdf.tobytes())
    chunks = chunk_pages(docs, chunk_size=20, chunk_overlap=4)
    assert docs[0].metadata["page"] == 1
    assert chunks and all(chunk.metadata["page"] == 1 for chunk in chunks)

def test_orchestrator_calls_only_selected_agent(monkeypatch):
    import core.orchestrator as module
    class Store:
        def similarity_search(self, query, k, filter):
            assert filter == {"doc_id": "doc-a"}
            from langchain_core.documents import Document
            return [Document(page_content="Paper evidence", metadata={"page": 4})]
    calls = []
    class Agent:
        def run(self, query, context):
            calls.append((query, context))
            return "Grounded answer"
    monkeypatch.setattr(module, "retrieve", lambda paper, query, k: paper.vectorstore.similarity_search(query, k, {"doc_id": paper.doc_id}))
    monkeypatch.setitem(module.AGENTS, Intent.PAPER_QA, Agent)
    answer = PaperOrchestrator(Paper("doc-a", "paper.pdf", 1, Store())).run(Intent.PAPER_QA, "question")
    assert answer == "Grounded answer"
    assert len(calls) == 1 and "[p. 4]" in calls[0][1]
