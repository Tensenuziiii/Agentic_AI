from dataclasses import dataclass
from enum import Enum
from pydantic import BaseModel, Field

class Intent(str, Enum):
    SUMMARY = "SUMMARY"
    CONCEPT_EXTRACTION = "CONCEPT_EXTRACTION"
    SLIDE_GENERATION = "SLIDE_GENERATION"
    VIVA_GENERATION = "VIVA_GENERATION"
    VIVA_PRACTICE = "VIVA_PRACTICE"
    PAPER_QA = "PAPER_QA"

@dataclass
class Paper:
    doc_id: str
    name: str
    page_count: int
    vectorstore: object

class AgentResponse(BaseModel):
    content: str = Field(min_length=1)
