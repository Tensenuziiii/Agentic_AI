from pydantic import BaseModel
from .schemas import Intent

class RoutedRequest(BaseModel):
    intent: Intent
    query: str

def route(text: str) -> RoutedRequest:
    from .router import detect_intent
    return RoutedRequest(intent=detect_intent(text), query=text)
