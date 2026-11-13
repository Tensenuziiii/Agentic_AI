from __future__ import annotations
import hashlib
import io
import os
import re
import uuid
import fitz
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document
from core.schemas import Paper

def extract_pages(pdf_bytes: bytes) -> list[Document]:
    if not pdf_bytes:
        raise ValueError("The uploaded PDF is empty.")
    try:
        pdf = fitz.open(stream=pdf_bytes, filetype="pdf")
    except Exception as exc:
        raise ValueError("This file could not be opened as a valid PDF.") from exc
    docs = [Document(page_content=p.get_text("text").strip(), metadata={"page": n + 1})
            for n, p in enumerate(pdf) if p.get_text("text").strip()]
    if not docs:
        raise ValueError("No selectable text was found. Scanned PDFs need OCR before upload.")
    return docs

def chunk_pages(pages: list[Document], chunk_size: int = 1000, chunk_overlap: int = 160) -> list[Document]:
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap, add_start_index=True)
    return splitter.split_documents(pages)

def ingest_pdf(pdf_bytes: bytes, name: str) -> Paper:
    pages = extract_pages(pdf_bytes)
    doc_id = hashlib.sha256(pdf_bytes).hexdigest()[:24]
    chunks = chunk_pages(pages)
    for chunk in chunks:
        chunk.metadata.update({"doc_id": doc_id, "chunk_id": str(uuid.uuid4())})
    embeddings = HuggingFaceEmbeddings(model_name=os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"))
    store = Chroma(collection_name="paper_" + re.sub("[^a-zA-Z0-9_]", "", doc_id), embedding_function=embeddings,
                   persist_directory=os.getenv("CHROMA_DIR", "./.chroma"))
    store.add_documents(chunks, ids=[x.metadata["chunk_id"] for x in chunks])
    return Paper(doc_id, name, len(pages), store)
