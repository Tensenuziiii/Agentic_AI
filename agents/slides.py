from .base import BaseAgent
class SlideGeneratorAgent(BaseAgent):
    task = "Create a presentation-ready slide outline. Format each slide as '## Slide N: Title' and concise bullets. Cover supported introduction, problem, objectives, methodology, architecture, implementation, results, conclusion, and references. Never add unsupported claims. Cite pages."
