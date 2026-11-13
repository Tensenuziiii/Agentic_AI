from .schemas import Intent

KEYWORDS = {
    Intent.SUMMARY: ("summary", "summarize", "overview"),
    Intent.CONCEPT_EXTRACTION: ("concept", "contribution", "methodology", "algorithm"),
    Intent.SLIDE_GENERATION: ("slide", "presentation", "powerpoint"),
    Intent.VIVA_GENERATION: ("viva", "examiner", "questions"),
    Intent.VIVA_PRACTICE: ("evaluate", "my answer", "practice answer", "mock viva"),
}

def detect_intent(text: str) -> Intent:
    lowered = text.lower()
    for intent, words in KEYWORDS.items():
        if any(word in lowered for word in words):
            return intent
    return Intent.PAPER_QA
