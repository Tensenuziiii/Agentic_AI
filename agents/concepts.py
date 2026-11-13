from .base import BaseAgent
class ConceptExtractorAgent(BaseAgent):
    task = "Explain the requested research concept using retrieved paper excerpts. Structure the answer with: Plain-language explanation; Technical explanation; How this paper uses it; A short analogy only when it is accurate. Cite page numbers for paper-specific claims. If the excerpts do not explain the concept, say what is missing rather than guessing."
