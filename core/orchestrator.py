from .schemas import Intent
from ingestion.retrieval import retrieve
from agents.summarizer import SummarizerAgent
from agents.concepts import ConceptExtractorAgent
from agents.slides import SlideGeneratorAgent
from agents.viva import VivaAgent

AGENTS = {Intent.SUMMARY: SummarizerAgent, Intent.CONCEPT_EXTRACTION: ConceptExtractorAgent,
          Intent.SLIDE_GENERATION: SlideGeneratorAgent, Intent.VIVA_GENERATION: VivaAgent,
          Intent.VIVA_PRACTICE: VivaAgent, Intent.PAPER_QA: VivaAgent}

class PaperOrchestrator:
    def __init__(self, paper):
        self.paper = paper
    def run(self, intent, query):
        intent = intent if isinstance(intent, Intent) else Intent(intent)
        docs = retrieve(self.paper, query, k=7)
        context = "\n\n".join(f"[p. {d.metadata.get('page', '?')}] {d.page_content}" for d in docs)
        if not context:
            return "The paper does not contain enough indexed text to answer this request."
        return AGENTS[intent]().run(query, context)
    @staticmethod
    def questions(result):
        import re
        return [re.sub(r"^\s*(?:[-*]|\d+[.)])\s*", "", line) for line in result.splitlines() if "?" in line][:12]
