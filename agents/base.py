from core.llm import make_chain
from core.schemas import AgentResponse
import os

class BaseAgent:
    task = "Answer the user using the provided excerpts."
    def run(self, query, context):
        try:
            result = make_chain(self.task).invoke({"task": self.task, "context": context, "query": query})
            return AgentResponse(content=result).content
        except Exception as exc:
            provider = os.getenv("LLM_PROVIDER", "ollama").strip().lower()
            detail = str(exc)
            key = os.getenv("OPENROUTER_API_KEY", "")
            if key:
                detail = detail.replace(key, "[redacted]")
            if provider == "openrouter":
                lower = detail.lower()
                if "401" in lower or "unauthorized" in lower or "authentication" in lower:
                    hint = "OpenRouter rejected the API key. Check OPENROUTER_API_KEY in .env."
                elif "429" in lower or "rate limit" in lower:
                    hint = "OpenRouter rate limit or account quota reached. Check your OpenRouter account and model limits."
                else:
                    hint = "Check the OpenRouter connection, selected model, and account access."
                raise RuntimeError(f"{hint} Details: {detail}") from exc
            raise RuntimeError(f"Could not reach Ollama. Confirm it is running, the model is pulled, and OLLAMA_MODEL is correct. Details: {detail}") from exc
