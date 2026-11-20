"""
Adaptive AI Learning Agent Service
Provides personalized career guidance using LangChain and OpenAI.
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ConversationBufferMemory
from langchain.tools import Tool
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from app.config import settings
from app.database import MongoDB
from app.models.agent_models import (
    ChatMessage, ChatRequest, AgentResponse, 
    ConversationHistory, ConversationContext, MessageRole
)
from app.services.skill_knowledge_graph import SkillKnowledgeGraph

logger = logging.getLogger(__name__)


class AdaptiveCareerAgent:
    """
    Adaptive AI agent for personalized career guidance.
    Uses LangChain with OpenAI and integrates with skill knowledge graph.
    """
    
    def __init__(self):
        """Initialize the AI agent."""
        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0.7,
            openai_api_key=settings.openai_api_key
        )
        self.skill_graph = SkillKnowledgeGraph()
        self.db = MongoDB.get_database()
        
    async def _get_conversation_history(self, user_id: str) -> List[ChatMessage]:
        """Retrieve conversation history from database."""
        try:
            conversation = await self.db.conversations.find_one({"user_id": user_id})
            if conversation:
                return [ChatMessage(**msg) for msg in conversation.get("messages", [])]
            return []
        except Exception as e:
            logger.error(f"Error retrieving conversation history: {e}")
            return []
    
    async def _save_message(self, user_id: str, message: ChatMessage, context: Optional[Dict] = None):
        """Save message to conversation history."""
        try:
            await self.db.conversations.update_one(
                {"user_id": user_id},
                {
                    "$push": {"messages": message.model_dump()},
                    "$set": {
                        "updated_at": datetime.utcnow(),
                        "context": context or {}
                    },
                    "$setOnInsert": {"created_at": datetime.utcnow()}
                },
                upsert=True
            )
        except Exception as e:
            logger.error(f"Error saving message: {e}")
    
    def _create_system_prompt(self, context: Optional[Dict] = None) -> str:
        """Create system prompt with context."""
        base_prompt = """You are SkillLens AI, an expert career guidance counselor specializing in helping engineering students prepare for their careers.

Your role is to:
1. Provide personalized, actionable career advice
2. Analyze skill gaps and recommend learning paths
3. Explain technical concepts clearly
4. Motivate and encourage students
5. Give specific, data-driven recommendations

Guidelines:
- Be encouraging and supportive
- Provide specific, actionable advice (not generic)
- Reference the student's current skills and goals when available
- Suggest concrete next steps
- Use examples and analogies when explaining concepts
- Keep responses concise but comprehensive
- Format responses with markdown for readability

Remember: 76% of students feel current guidance is generic. Make your advice SPECIFIC and PERSONALIZED."""

        if context:
            context_info = "\n\nCurrent Context:"
            if context.get("target_role"):
                context_info += f"\n- Target Role: {context['target_role']}"
            if context.get("current_skills"):
                context_info += f"\n- Current Skills: {', '.join(context['current_skills'])}"
            if context.get("skill_gaps"):
                context_info += f"\n- Identified Skill Gaps: {', '.join(context['skill_gaps'])}"
            base_prompt += context_info
        
        return base_prompt
    
    def _get_skill_info_tool(self) -> Tool:
        """Create tool for querying skill information."""
        async def get_skill_info(skill_name: str) -> str:
            """Get information about a skill including prerequisites and related skills."""
            try:
                # Query Neo4j for skill information
                skill_info = await self.skill_graph.get_skill_details(skill_name)
                if skill_info:
                    prereqs = skill_info.get("prerequisites", [])
                    related = skill_info.get("related_skills", [])
                    
                    result = f"Skill: {skill_name}\n"
                    if prereqs:
                        result += f"Prerequisites: {', '.join(prereqs)}\n"
                    if related:
                        result += f"Related Skills: {', '.join(related)}\n"
                    return result
                return f"No detailed information found for {skill_name}"
            except Exception as e:
                logger.error(f"Error getting skill info: {e}")
                return f"Unable to retrieve information for {skill_name}"
        
        return Tool(
            name="get_skill_info",
            func=get_skill_info,
            description="Get detailed information about a specific skill, including prerequisites and related skills. Input should be the skill name."
        )
    
    def _get_learning_path_tool(self) -> Tool:
        """Create tool for generating learning paths."""
        async def suggest_learning_path(target_skill: str) -> str:
            """Suggest a learning path for acquiring a target skill."""
            try:
                # Get skill dependencies from knowledge graph
                path = await self.skill_graph.get_learning_path(target_skill)
                if path:
                    steps = " → ".join(path)
                    return f"Recommended learning path for {target_skill}: {steps}"
                return f"No learning path found for {target_skill}"
            except Exception as e:
                logger.error(f"Error generating learning path: {e}")
                return f"Unable to generate learning path for {target_skill}"
        
        return Tool(
            name="suggest_learning_path",
            func=suggest_learning_path,
            description="Suggest a step-by-step learning path for acquiring a target skill. Input should be the skill name."
        )
    
    async def chat(self, request: ChatRequest) -> AgentResponse:
        """
        Process chat message and generate response.
        
        Args:
            request: Chat request with user message and context
            
        Returns:
            Agent response with message and metadata
        """
        try:
            # Get conversation history
            history = await self._get_conversation_history(request.user_id)
            
            # Save user message
            user_message = ChatMessage(
                role=MessageRole.USER,
                content=request.message,
                timestamp=datetime.utcnow()
            )
            await self._save_message(request.user_id, user_message, request.context)
            
            # Create system prompt with context
            system_prompt = self._create_system_prompt(request.context)
            
            # Build message history for LLM
            messages = [SystemMessage(content=system_prompt)]
            
            # Add conversation history (last 10 messages for context)
            for msg in history[-10:]:
                if msg.role == MessageRole.USER:
                    messages.append(HumanMessage(content=msg.content))
                elif msg.role == MessageRole.ASSISTANT:
                    messages.append(AIMessage(content=msg.content))
            
            # Add current user message
            messages.append(HumanMessage(content=request.message))
            
            # Generate response
            response = await self.llm.ainvoke(messages)
            response_content = response.content
            
            # Save assistant message
            assistant_message = ChatMessage(
                role=MessageRole.ASSISTANT,
                content=response_content,
                timestamp=datetime.utcnow()
            )
            await self._save_message(request.user_id, assistant_message, request.context)
            
            # Generate suggestions based on context
            suggestions = self._generate_suggestions(request.message, request.context)
            
            # Check if learning path is available
            learning_path_available = bool(request.context and request.context.get("skill_gaps"))
            
            return AgentResponse(
                message=response_content,
                conversation_id=request.user_id,
                suggestions=suggestions,
                learning_path_available=learning_path_available,
                metadata={
                    "model": "gpt-3.5-turbo",
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
            
        except Exception as e:
            logger.error(f"Error in chat: {e}")
            return AgentResponse(
                message="I apologize, but I encountered an error processing your request. Please try again.",
                conversation_id=request.user_id,
                suggestions=["Try rephrasing your question", "Check your connection"],
                learning_path_available=False,
                metadata={"error": str(e)}
            )
    
    def _generate_suggestions(self, message: str, context: Optional[Dict]) -> List[str]:
        """Generate contextual suggestions for next questions."""
        suggestions = []
        
        message_lower = message.lower()
        
        if "skill" in message_lower or "learn" in message_lower:
            suggestions.append("Generate a personalized learning path")
            suggestions.append("What are the prerequisites for this skill?")
        
        if "resume" in message_lower:
            suggestions.append("Analyze my skill gaps")
            suggestions.append("How can I improve my resume?")
        
        if "job" in message_lower or "career" in message_lower:
            suggestions.append("What skills do I need for this role?")
            suggestions.append("Show me similar career paths")
        
        if not suggestions:
            suggestions = [
                "Generate a learning path for me",
                "Analyze my resume",
                "What skills are in demand?"
            ]
        
        return suggestions[:3]  # Return top 3 suggestions
    
    async def get_conversation_history(self, user_id: str) -> Optional[ConversationHistory]:
        """Get full conversation history for a user."""
        try:
            conversation = await self.db.conversations.find_one({"user_id": user_id})
            if conversation:
                return ConversationHistory(
                    user_id=conversation["user_id"],
                    conversation_id=conversation.get("_id", user_id),
                    messages=[ChatMessage(**msg) for msg in conversation.get("messages", [])],
                    context=ConversationContext(**conversation.get("context", {"user_id": user_id})),
                    created_at=conversation.get("created_at", datetime.utcnow()),
                    updated_at=conversation.get("updated_at", datetime.utcnow())
                )
            return None
        except Exception as e:
            logger.error(f"Error getting conversation history: {e}")
            return None
    
    async def clear_conversation(self, user_id: str) -> bool:
        """Clear conversation history for a user."""
        try:
            result = await self.db.conversations.delete_one({"user_id": user_id})
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Error clearing conversation: {e}")
            return False


# Singleton instance
_agent_instance = None

def get_agent() -> AdaptiveCareerAgent:
    """Get singleton instance of the agent."""
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = AdaptiveCareerAgent()
    return _agent_instance
