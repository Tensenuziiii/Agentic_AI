from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
import os
import urllib.error
import urllib.request
import json

SYSTEM = """You are an academic research-paper assistant. Use only the supplied paper excerpts. Never invent facts, results, references, or page citations. Say clearly when the paper does not contain an answer. Include citations as [p. N] using the provided page metadata. Be precise and accessible."""

def make_chain(task: str):
    prompt = ChatPromptTemplate.from_messages([("system", SYSTEM), ("human", "Task: {task}\n\nPaper excerpts:\n{context}\n\nUser request:\n{query}")])
    provider = os.getenv("LLM_PROVIDER", "ollama").strip().lower()
    if provider == "openrouter":
        api_key = os.getenv("OPENROUTER_API_KEY", "").strip()
        if not api_key:
            raise RuntimeError("LLM_PROVIDER is openrouter, but OPENROUTER_API_KEY is not set in the local .env file.")
        llm = ChatOpenAI(
            model=os.getenv("OPENROUTER_MODEL", "openrouter/free"),
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1",
            temperature=0.2,
        )
    elif provider == "ollama":
        llm = ChatOllama(model=os.getenv("OLLAMA_MODEL", "llama3.2"), base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"), temperature=0.2)
    else:
        raise ValueError(f"Unsupported LLM_PROVIDER '{provider}'. Choose 'ollama' or 'openrouter'.")
    return prompt | llm | StrOutputParser()

def provider_status() -> tuple[bool, str]:
    provider = os.getenv("LLM_PROVIDER", "ollama").strip().lower()
    if provider == "openrouter":
        if not os.getenv("OPENROUTER_API_KEY", "").strip():
            return False, "OpenRouter selected, but OPENROUTER_API_KEY is missing from .env."
        return True, f"OpenRouter configured · {os.getenv('OPENROUTER_MODEL', 'openrouter/free')}"
    if provider == "ollama":
        return ollama_status()
    return False, f"Unsupported LLM_PROVIDER `{provider}`. Choose ollama or openrouter."

def ollama_status() -> tuple[bool, str]:
    """Return local Ollama/model readiness without starting a generation."""
    base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
    model = os.getenv("OLLAMA_MODEL", "llama3.2")
    try:
        with urllib.request.urlopen(base_url + "/api/tags", timeout=1.5) as response:
            installed = [item.get("name", "") for item in json.loads(response.read()).get("models", [])]
        if not any(item == model or item.startswith(model + ":") for item in installed):
            return False, f"Ollama is running, but model `{model}` is not installed. Run `ollama pull {model}`."
        return True, f"Ollama ready · {model}"
    except (urllib.error.URLError, TimeoutError, ValueError, OSError):
        return False, f"Ollama is not responding at `{base_url}`. Start Ollama, then run `ollama pull {model}`."
