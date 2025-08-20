import logging
import uuid
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
import instructor
from jinja2 import Environment, FileSystemLoader
from google.genai import Client
from instructor import Mode

from .models.chat_models import (
    ChatMessage, ChatContext, ConversationSummary, ConversationHistory,
    MessageRole, ChatRequest, ChatResponse
)

logger = logging.getLogger(__name__)

class ChatService:
    """
    Service for handling chat conversations with context from IPO analysis
    Includes conversation memory and summarization capabilities
    """
    
    def __init__(self, gemini_api_key: str):
        """Initialize chat service with Gemini API"""
        self.genai_client = Client(api_key=gemini_api_key)
        
        # Initialize Gemini model with Instructor
        self.model = instructor.from_genai(
            client=self.genai_client,
            mode=Mode.GENAI_STRUCTURED_OUTPUTS
        )
        
        # Initialize Jinja2 environment for prompts
        template_dir = "./prompts"
        self.jinja_env = Environment(loader=FileSystemLoader(template_dir))
        
        # In-memory storage for conversations (in production, use a database)
        self.conversations: Dict[str, ConversationHistory] = {}
        self.chat_contexts: Dict[str, ChatContext] = {}
    
    def store_analysis_context(self, analysis_id: str, full_text: str, 
                             extracted_content: Dict[str, Any], 
                             analysis_results: Dict[str, Any]) -> None:
        """Store analysis context for chat conversations"""
        try:
            company_name = None
            if analysis_results.get('company_metadata'):
                company_name = analysis_results['company_metadata'].get('company_name')
            
            context = ChatContext(
                analysis_id=analysis_id,
                company_name=company_name,
                full_text=full_text,
                extracted_content=extracted_content,
                analysis_results=analysis_results,
                conversation_summary=None
            )
            
            self.chat_contexts[analysis_id] = context
            logger.info(f"Stored chat context for analysis {analysis_id}")
            
        except Exception as e:
            logger.error(f"Error storing analysis context: {str(e)}")
            raise
    
    async def chat(self, request: ChatRequest) -> ChatResponse:
        """
        Process a chat message with full context and memory
        """
        try:
            # Get or create conversation
            conversation_id = request.conversation_id or str(uuid.uuid4())
            
            if conversation_id not in self.conversations:
                self.conversations[conversation_id] = ConversationHistory(
                    conversation_id=conversation_id,
                    analysis_id=request.analysis_id,
                    summary=None
                )
            
            conversation = self.conversations[conversation_id]
            
            # Get analysis context
            if request.analysis_id not in self.chat_contexts:
                raise ValueError(f"No context found for analysis {request.analysis_id}")
            
            context = self.chat_contexts[request.analysis_id]
            
            # Add user message to conversation
            user_message = ChatMessage(
                id=str(uuid.uuid4()),
                role=MessageRole.USER,
                content=request.message,
                analysis_id=request.analysis_id
            )
            conversation.messages.append(user_message)
            
            # Update conversation summary if needed
            if len(conversation.messages) > 6:  # Update summary every 6 messages
                conversation.summary = await self._update_conversation_summary(conversation, context)
            
            # Generate response
            response_content = await self._generate_response(
                user_message=request.message,
                context=context,
                conversation=conversation
            )
            
            # Create assistant response
            response_message = ChatMessage(
                id=str(uuid.uuid4()),
                role=MessageRole.ASSISTANT,
                content=response_content,
                analysis_id=request.analysis_id
            )
            conversation.messages.append(response_message)
            conversation.updated_at = datetime.now()
            
            # Extract sources referenced (simple keyword matching)
            sources_referenced = self._extract_sources_referenced(response_content, context)
            
            return ChatResponse(
                message_id=response_message.id,
                content=response_content,
                conversation_id=conversation_id,
                analysis_id=request.analysis_id,
                sources_referenced=sources_referenced
            )
            
        except Exception as e:
            logger.error(f"Error processing chat message: {str(e)}")
            raise
    
    async def _generate_response(self, user_message: str, context: ChatContext, 
                               conversation: ConversationHistory) -> str:
        """Generate AI response using context and conversation history"""
        try:
            # Prepare conversation history (last 10 messages to avoid token limits)
            recent_messages = conversation.messages[-10:] if len(conversation.messages) > 10 else conversation.messages
            
            # Build conversation history string
            conversation_history = ""
            for msg in recent_messages[:-1]:  # Exclude the current user message
                role_name = "User" if msg.role == MessageRole.USER else "Assistant"
                conversation_history += f"{role_name}: {msg.content}\n\n"
            
            # Add conversation summary if available
            summary_context = ""
            if conversation.summary:
                summary_context = f"""
## Previous Conversation Summary
Key Topics: {', '.join(conversation.summary.key_topics)}
Important Questions: {', '.join(conversation.summary.important_questions)}
Key Insights: {', '.join(conversation.summary.key_insights)}
User Concerns: {', '.join(conversation.summary.user_concerns)}
Summary: {conversation.summary.summary_text}
"""
            
            # Load chat prompt template
            template = self.jinja_env.get_template("chat_prompt.j2")
            prompt = template.render(
                company_name=context.company_name or "the company",
                user_message=user_message,
                full_text=context.full_text,
                extracted_content=context.extracted_content,
                analysis_results=context.analysis_results,
                conversation_history=conversation_history,
                summary_context=summary_context
            )
            
            # Generate response using Gemini
            response = await asyncio.to_thread(
                self.genai_client.models.generate_content,
                model="gemini-2.5-flash",
                contents=prompt,
                config={
                    "temperature": 0.3,
                    "max_output_tokens": 1000,
                }
            )
            
            return response.text.strip() if response.text else "I apologize, but I couldn't generate a response."
            
        except Exception as e:
            logger.error(f"Error generating chat response: {str(e)}")
            return "I apologize, but I encountered an error while processing your question. Please try again."
    
    async def _update_conversation_summary(self, conversation: ConversationHistory, 
                                         context: ChatContext) -> ConversationSummary:
        """Update conversation summary for efficient context management"""
        try:
            # Get recent messages for summarization
            messages_text = ""
            for msg in conversation.messages[-10:]:  # Last 10 messages
                role_name = "User" if msg.role == MessageRole.USER else "Assistant"
                messages_text += f"{role_name}: {msg.content}\n\n"
            
            # Create summarization prompt
            summary_prompt = f"""
Please analyze the following conversation about {context.company_name or "the company"}'s IPO readiness analysis and create a concise summary:

{messages_text}

Extract:
1. Key topics discussed (max 5)
2. Important questions asked by the user (max 5)
3. Key insights shared (max 5)
4. Main user concerns or focus areas (max 5)
5. A concise summary paragraph (max 150 words)

Provide the response in a structured format.
"""
            
            response = await asyncio.to_thread(
                self.genai_client.models.generate_content,
                model="gemini-2.0-flash",
                contents=summary_prompt,
                config={
                    "temperature": 0.3,
                    "max_output_tokens": 500,
                }
            )
            
            # Parse response (simplified - in production, use structured outputs)
            response_text = response.text.strip() if response.text else ""
            
            # Create summary object (simplified parsing)
            summary = ConversationSummary(
                key_topics=self._extract_list_from_response(response_text, "Key topics"),
                important_questions=self._extract_list_from_response(response_text, "Important questions"),
                key_insights=self._extract_list_from_response(response_text, "Key insights"),
                user_concerns=self._extract_list_from_response(response_text, "user concerns"),
                summary_text=self._extract_summary_from_response(response_text),
                last_updated=datetime.now()
            )
            
            return summary
            
        except Exception as e:
            logger.error(f"Error updating conversation summary: {str(e)}")
            # Return empty summary on error
            return ConversationSummary(
                summary_text="Summary unavailable due to processing error",
                last_updated=datetime.now()
            )
    
    def _extract_sources_referenced(self, response: str, context: ChatContext) -> List[str]:
        """Extract which parts of the analysis were referenced in the response"""
        sources = []
        
        # Check for references to different parts of the analysis
        response_lower = response.lower()
        
        if any(word in response_lower for word in ['score', 'scoring', 'rating']):
            sources.append("IPO Scores")
        
        if any(word in response_lower for word in ['financial', 'revenue', 'profit', 'funding']):
            sources.append("Financial Highlights")
        
        if any(word in response_lower for word in ['risk', 'concern', 'weakness']):
            sources.append("Risk Assessment")
        
        if any(word in response_lower for word in ['strength', 'advantage', 'positive']):
            sources.append("Strengths Analysis")
        
        if any(word in response_lower for word in ['recommendation', 'suggest', 'should']):
            sources.append("Recommendations")
        
        if any(word in response_lower for word in ['competitive', 'market', 'industry']):
            sources.append("Market Analysis")
        
        return sources
    
    def _extract_list_from_response(self, response: str, section: str) -> List[str]:
        """Extract list items from AI response (simplified parsing)"""
        # This is a simplified implementation - in production, use structured outputs
        lines = response.split('\n')
        items = []
        in_section = False
        
        for line in lines:
            if section.lower() in line.lower():
                in_section = True
                continue
            
            if in_section and line.strip():
                if line.strip().startswith(('-', '•', '*', '1.', '2.', '3.', '4.', '5.')):
                    item = line.strip().lstrip('-•*123456789. ').strip()
                    if item:
                        items.append(item)
                elif not line.strip().startswith(('Key', 'Important', 'Main', 'Summary')):
                    break
        
        return items[:5]  # Limit to 5 items
    
    def _extract_summary_from_response(self, response: str) -> str:
        """Extract summary paragraph from AI response"""
        # Look for summary section
        lines = response.split('\n')
        summary_lines = []
        in_summary = False
        
        for line in lines:
            if 'summary' in line.lower() and ':' in line:
                in_summary = True
                # Check if summary is on the same line
                if line.split(':')[1].strip():
                    summary_lines.append(line.split(':')[1].strip())
                continue
            
            if in_summary:
                if line.strip() and not line.strip().startswith(('Key', 'Important', 'Main')):
                    summary_lines.append(line.strip())
                elif line.strip().startswith(('Key', 'Important', 'Main')):
                    break
        
        summary = ' '.join(summary_lines).strip()
        return summary if summary else "Conversation summary unavailable"
    
    def get_conversation_history(self, conversation_id: str) -> Optional[ConversationHistory]:
        """Get conversation history by ID"""
        return self.conversations.get(conversation_id)
    
    def get_conversations_for_analysis(self, analysis_id: str) -> List[ConversationHistory]:
        """Get all conversations for a specific analysis"""
        return [conv for conv in self.conversations.values() if conv.analysis_id == analysis_id]