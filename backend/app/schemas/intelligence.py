from pydantic import BaseModel, Field
from typing import Optional


class ActionItem(BaseModel):
    id: int
    task: str
    owner: Optional[str] = None
    due_date: Optional[str] = None
    confidence: float = Field(ge=0.0, le=1.0)
    source_timestamp: str
    status: str


class MeetingRequest(BaseModel):
    id: int
    topic: str
    suggested_date: Optional[str] = None
    suggested_time: Optional[str] = None
    confidence: float = Field(ge=0.0, le=1.0)
    source_timestamp: str
    status: str


class Decision(BaseModel):
    id: int
    decision: str
    confidence: float = Field(ge=0.0, le=1.0)
    source_timestamp: str
    status: str = "detected"


class OpenQuestion(BaseModel):
    id: int
    question: str
    confidence: float = Field(ge=0.0, le=1.0)
    source_timestamp: str
    status: str = "open"

class Risk(BaseModel):
    id: int
    risk: str
    confidence: float = Field(ge=0.0, le=1.0)
    source_timestamp: str
    status: str = "open"
    
class MeetingIntelligence(BaseModel):
    summary: list[str] = Field(default_factory=list)
    action_items: list[ActionItem] = Field(default_factory=list)
    meeting_requests: list[MeetingRequest] = Field(default_factory=list)
    decisions: list[Decision] = Field(default_factory=list)
    open_questions: list[OpenQuestion] = Field(default_factory=list)
    risks: list[Risk] = Field(default_factory=list)