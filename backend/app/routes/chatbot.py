"""
Chatbot API routes — exposes endpoints for website knowledge queries,
conversational answers, and suggested inquiry prompts.
"""

import logging
from typing import Optional
from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.services.chatbot_service import chatbot_service

logger = logging.getLogger(__name__)

router = APIRouter()


class ChatMessage(BaseModel):
    role: str = Field(description="Role of the speaker: 'user' or 'assistant'")
    content: str = Field(description="Message body text")


class ChatQueryRequest(BaseModel):
    message: str = Field(description="User prompt or question about SatyaSutra")
    history: Optional[list[ChatMessage]] = Field(default=None, description="Recent conversation turns")


class ChatQueryResponse(BaseModel):
    answer: str
    sources: list[str] = Field(default_factory=list)
    related_links: list[str] = Field(default_factory=list)
    suggested_followups: list[str] = Field(default_factory=list)
    confidence: float = 1.0


@router.post("/ask", response_model=ChatQueryResponse)
async def ask_chatbot(payload: ChatQueryRequest):
    """
    Query the SatyaSutra website model. Returns an auditable,
    accurate answer with sources and navigation links.
    """
    history_dicts = None
    if payload.history:
        history_dicts = [{"role": msg.role, "content": msg.content} for msg in payload.history]

    result = chatbot_service.answer_query(
        query=payload.message,
        conversation_history=history_dicts,
    )

    return ChatQueryResponse(
        answer=result.get("answer", ""),
        sources=result.get("sources", []),
        related_links=result.get("related_links", []),
        suggested_followups=result.get("suggested_followups", []),
        confidence=result.get("confidence", 1.0),
    )


@router.get("/suggestions")
async def get_suggestions():
    """Return pre-configured popular inquiry prompts."""
    return {
        "suggestions": chatbot_service.get_suggested_questions(),
    }
