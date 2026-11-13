from .base import BaseAgent
class VivaAgent(BaseAgent):
    task = "For viva generation, create questions with model answers, balanced across requested difficulty and cite pages. For answer evaluation, score out of 10, list correct/missing points, and provide an improved answer. For paper questions, answer directly and cite pages."
