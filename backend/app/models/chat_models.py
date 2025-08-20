from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum

class MessageRole(str, Enum):
    """Chat message roles"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

class ChatMessage(BaseModel):
    """Individual chat message"""
    id: str = Field(..., description="Unique message identifier")
    role: MessageRole = Field(..., description="Message role (user/assistant/system)")
    content: str = Field(..., description="Message content")
    timestamp: datetime = Field(default_factory=datetime.now, description="Message timestamp")
    analysis_id: Optional[str] = Field(None, description="Related analysis ID for context")

class ConversationSummary(BaseModel):
    """Summarized conversation context"""
    key_topics: List[str] = Field(default_factory=list, description="Main topics discussed")
    important_questions: List[str] = Field(default_factory=list, description="Important questions asked")
    key_insights: List[str] = Field(default_factory=list, description="Key insights shared")
    user_concerns: List[str] = Field(default_factory=list, description="User concerns or focus areas")
    summary_text: str = Field(..., description="Concise summary of the conversation")
    last_updated: datetime = Field(default_factory=datetime.now, description="When summary was last updated")

class ChatContext(BaseModel):
    """Complete context for chat conversation"""
    analysis_id: str = Field(..., description="Related IPO analysis ID")
    company_name: Optional[str] = Field(None, description="Company name for context")
    full_text: str = Field(..., description="Full extracted PDF text")
    extracted_content: Dict[str, Any] = Field(..., description="Structured extracted content")
    analysis_results: Dict[str, Any] = Field(..., description="IPO analysis results")
    conversation_summary: Optional[ConversationSummary] = Field(None, description="Conversation summary")

class ChatRequest(BaseModel):
    """Chat message request"""
    message: str = Field(..., description="User message")
    analysis_id: str = Field(..., description="Related analysis ID")
    conversation_id: Optional[str] = Field(None, description="Conversation ID for continuity")

class ChatResponse(BaseModel):
    """Chat message response"""
    message_id: str = Field(..., description="Response message ID")
    content: str = Field(..., description="Assistant response content")
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp")
    conversation_id: str = Field(..., description="Conversation ID")
    analysis_id: str = Field(..., description="Related analysis ID")
    sources_referenced: List[str] = Field(default_factory=list, description="Parts of analysis referenced")

class ConversationHistory(BaseModel):
    """Complete conversation history"""
    conversation_id: str = Field(..., description="Unique conversation identifier")
    analysis_id: str = Field(..., description="Related analysis ID")
    messages: List[ChatMessage] = Field(default_factory=list, description="All messages in conversation")
    summary: Optional[ConversationSummary] = Field(None, description="Conversation summary")
    created_at: datetime = Field(default_factory=datetime.now, description="Conversation start time")
    updated_at: datetime = Field(default_factory=datetime.now, description="Last message time")

class ChatError(BaseModel):
    """Chat error response"""
    error: str = Field(..., description="Error message")
    error_type: str = Field(..., description="Type of error")
    conversation_id: Optional[str] = Field(None, description="Related conversation ID")
    timestamp: datetime = Field(default_factory=datetime.now, description="Error timestamp")