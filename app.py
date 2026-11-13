"""Streamlit entry point for Paper-to-Presentation & Viva Agent."""
from __future__ import annotations

import streamlit as st
import os
from dotenv import load_dotenv

load_dotenv()

from core.orchestrator import PaperOrchestrator
from core.router import detect_intent
from core.llm import provider_status
from ingestion.pipeline import ingest_pdf
from services.presentation import make_presentation
from ui.styles import apply_styles

st.set_page_config(page_title="Paper-to-Presentation & Viva Agent", page_icon="📚", layout="wide")
apply_styles()
st.markdown("""<div class="hero"><div class="hero-kicker">Research companion · local AI</div>
<div class="hero-title">Paper to presentation.<br>Paper to confident answers.</div>
<div class="hero-copy">Upload one paper to explore its ideas, build an editable slide deck, and prepare for your viva with answers grounded in the source.</div></div>""", unsafe_allow_html=True)
@st.cache_data(ttl=20, show_spinner=False)
def cached_provider_status():
    return provider_status()

model_ready, model_message = cached_provider_status()

with st.sidebar:
    st.header("Your paper")
    uploaded = st.file_uploader("Upload a research paper", type=["pdf"])
    if uploaded and st.button("Process paper", type="primary", use_container_width=True):
        with st.spinner("Extracting, chunking, embedding, and indexing the paper…"):
            try:
                st.session_state.paper = ingest_pdf(uploaded.getvalue(), uploaded.name)
                st.session_state.messages = []
                for key in ("summary", "concepts", "concept_explanation", "concept_explanation_title", "slide_outline", "pptx", "viva", "viva_questions", "viva_index", "viva_scores"):
                    st.session_state.pop(key, None)
                st.success(f"Indexed {st.session_state.paper.page_count} pages")
            except Exception as exc:
                st.error(str(exc))
    paper = st.session_state.get("paper")
    if paper:
        st.success(f"Ready · {paper.page_count} pages")
        st.caption(paper.name)
    else:
        st.info("Upload a text-based PDF to begin.")
    st.divider()
    st.caption("Local-first · Ollama · ChromaDB")
    if model_ready:
        st.success(model_message)
    else:
        st.warning(model_message)
        with st.expander("Set up the local model"):
            st.code("ollama pull llama3.2\nollama serve", language="powershell")

if not st.session_state.get("paper"):
    st.info("Upload and process a research paper in the sidebar to unlock the workspace.")
    st.stop()

paper = st.session_state.paper
orch = PaperOrchestrator(paper)
left, middle, right = st.columns(3)
with left:
    st.metric("Paper", "Indexed", help=paper.name)
with middle:
    st.metric("Pages", paper.page_count)
with right:
    provider_id = os.getenv("LLM_PROVIDER", "ollama").strip().lower()
    provider_name = {"openrouter": "OpenRouter", "ollama": "Ollama"}.get(provider_id, provider_id)
    st.metric("AI provider", provider_name)
    st.caption("Configured" if model_ready else "Unavailable")
tabs = st.tabs(["Overview", "Concepts", "Presentation", "Viva practice", "Ask your paper"])

with tabs[0]:
    st.subheader("Paper summary")
    depth = st.radio("Summary depth", ["Brief", "Detailed"], horizontal=True, key="summary_depth")
    if st.button("Generate summary", key="summary_btn"):
        with st.spinner("Reading relevant sections…"):
            try:
                st.session_state.summary = orch.run("SUMMARY", "Give a " + depth.lower() + " structured summary.")
            except Exception as exc:
                st.error(str(exc))
    if st.session_state.get("summary"):
        st.markdown(st.session_state.summary)

with tabs[1]:
    st.subheader("Understand the ideas behind the paper")
    st.markdown("Enter a term, method, or algorithm from your paper. The explanation will separate a plain-language description from the technical meaning.")
    concept_col, level_col = st.columns([2, 1])
    with concept_col:
        concept_name = st.text_input("What should I explain?", placeholder="e.g. contrastive learning, attention mechanism…", key="concept_name")
    with level_col:
        explanation_level = st.selectbox("Explanation style", ["Beginner friendly", "Technical", "Both"], key="explanation_level")
    explain_col, extract_col = st.columns([1, 1])
    with explain_col:
        explain_clicked = st.button("Explain this concept", type="primary", key="explain_concept_btn", use_container_width=True, disabled=not bool(concept_name.strip()))
    with extract_col:
        extract_clicked = st.button("Explore key concepts", key="concept_btn", use_container_width=True)
    if explain_clicked:
        explain_query = f"Explain the concept '{concept_name.strip()}' in a {explanation_level.lower()} way. Define it, explain its technical operation, explain how the uploaded paper uses it, and give a simple accurate analogy if possible. Cite paper pages."
        with st.spinner("Extracting concepts…"):
            try:
                st.session_state.concept_explanation = orch.run("CONCEPT_EXTRACTION", explain_query)
                st.session_state.concept_explanation_title = concept_name.strip()
            except Exception as exc:
                st.error(str(exc))
    if extract_clicked:
        with st.spinner("Finding the paper’s central ideas…"):
            try:
                st.session_state.concepts = orch.run("CONCEPT_EXTRACTION", "Identify the paper's most important concepts, algorithms, methods, contributions and findings. Explain technical terms in accessible language. Cite pages.")
            except Exception as exc:
                st.error(str(exc))
    if st.session_state.get("concept_explanation"):
        st.markdown(f"#### {st.session_state.get('concept_explanation_title', 'Concept explanation')}")
        st.markdown(st.session_state.concept_explanation)
    if st.session_state.get("concepts"):
        st.divider()
        st.markdown("#### Key ideas found in the paper")
        st.markdown(st.session_state.concepts)

with tabs[2]:
    st.subheader("Presentation generator")
    slide_count = st.slider("Target slide count", 5, 14, 9)
    if st.button("Generate presentation", type="primary", key="slides_btn"):
        with st.spinner("Building presentation from retrieved paper content…"):
            try:
                content = orch.run("SLIDE_GENERATION", f"Create content for {slide_count} presentation slides covering introduction, problem, objectives, method, architecture, results, conclusion and references only where supported.")
                st.session_state.pptx = make_presentation(paper.name, content)
                st.session_state.slide_outline = content
            except Exception as exc:
                st.error(str(exc))
    if st.session_state.get("slide_outline"):
        st.markdown(st.session_state.slide_outline)
    if st.session_state.get("pptx"):
        st.download_button("Download editable PowerPoint", st.session_state.pptx, file_name="paper_presentation.pptx", mime="application/vnd.openxmlformats-officedocument.presentationml.presentation")

with tabs[3]:
    st.subheader("Viva preparation")
    level = st.selectbox("Difficulty", ["Basic", "Intermediate", "Advanced"])
    if st.button("Generate viva questions", key="viva_btn"):
        with st.spinner("Preparing grounded questions and model answers…"):
            try:
                st.session_state.viva = orch.run("VIVA_GENERATION", f"Generate 5 {level.lower()} viva questions with concise model answers and paper page references.")
                st.session_state.viva_questions = orch.questions(st.session_state.viva)
                st.session_state.viva_index = 0
                st.session_state.viva_scores = []
            except Exception as exc:
                st.error(str(exc))
    if st.session_state.get("viva"):
        st.markdown(st.session_state.viva)
    qs = st.session_state.get("viva_questions", [])
    if qs and st.session_state.viva_index < len(qs):
        i = st.session_state.viva_index
        st.markdown(f"**Practice {i+1}/{len(qs)}:** {qs[i]}")
        answer = st.text_area("Your answer", key=f"answer_{i}")
        prior = st.session_state.get("viva_scores", [])
        if len(prior) > i:
            st.markdown(prior[i])
            if st.button("Next question", key=f"next_{i}"):
                st.session_state.viva_index += 1
                st.rerun()
        elif st.button("Evaluate answer", key=f"eval_{i}") and answer.strip():
            with st.spinner("Evaluating against the paper…"):
                try:
                    result = orch.run("VIVA_PRACTICE", f"Evaluate this student's response to the viva question. Give score out of 10, missing points, and a stronger answer.\nQuestion: {qs[i]}\nStudent answer: {answer}")
                    st.session_state.viva_scores.append(result)
                    st.markdown(result)
                except Exception as exc:
                    st.error(str(exc))
    elif qs:
        st.success("Practice complete. Performance report")
        scores = st.session_state.get("viva_scores", [])
        import re
        marks = [float(value) for result in scores for value in re.findall(r"(?:score|mark)[^\d]{0,20}(\d+(?:\.\d+)?)\s*/\s*10", result, re.I)]
        if marks:
            st.metric("Average score", f"{sum(marks)/len(marks):.1f}/10")
        for result in scores:
            st.markdown(result)

with tabs[4]:
    st.subheader("Ask your paper")
    for msg in st.session_state.get("messages", []):
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    question = st.chat_input("Ask a question grounded in the uploaded paper")
    if question:
        st.session_state.messages.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.markdown(question)
        with st.chat_message("assistant"):
            with st.spinner("Searching the paper…"):
                try:
                    answer = orch.run(detect_intent(question), question)
                    st.markdown(answer)
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                except Exception as exc:
                    st.error(str(exc))
