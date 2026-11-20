"""
Test script for AI Agent functionality
Run this to verify the agent is working correctly
"""

import asyncio
from app.services.ai_agent import get_agent
from app.services.learning_path_generator import get_learning_path_generator
from app.models.agent_models import ChatRequest, LearningPathRequest

async def test_agent_chat():
    """Test basic chat functionality"""
    print("=" * 60)
    print("Testing AI Agent Chat")
    print("=" * 60)
    
    agent = get_agent()
    
    # Test message
    request = ChatRequest(
        user_id="test_user_123",
        message="I want to become a full-stack developer. What skills do I need?",
        context={
            "target_role": "Full Stack Developer",
            "current_skills": ["Python", "HTML"]
        }
    )
    
    print(f"\nUser: {request.message}")
    print("\nAgent: ", end="", flush=True)
    
    response = await agent.chat(request)
    print(response.message)
    print(f"\nSuggestions: {response.suggestions}")
    print(f"Learning path available: {response.learning_path_available}")
    
    return response

async def test_learning_path():
    """Test learning path generation"""
    print("\n" + "=" * 60)
    print("Testing Learning Path Generation")
    print("=" * 60)
    
    generator = get_learning_path_generator()
    
    request = LearningPathRequest(
        user_id="test_user_123",
        target_role="Full Stack Developer",
        current_skills=["Python", "HTML"],
        experience_level="Beginner"
    )
    
    print(f"\nTarget Role: {request.target_role}")
    print(f"Current Skills: {', '.join(request.current_skills)}")
    print(f"Experience Level: {request.experience_level}\n")
    
    path = await generator.generate_learning_path(request)
    
    print(f"Total Estimated Time: {path.total_estimated_time}")
    print(f"\nLearning Path ({len(path.steps)} steps):\n")
    
    for step in path.steps:
        print(f"{step.step_number}. {step.skill} ({step.difficulty})")
        print(f"   Time: {step.estimated_time}")
        print(f"   Prerequisites: {', '.join(step.prerequisites) if step.prerequisites else 'None'}")
        print(f"   Resources: {len(step.resources)} available")
        print()
    
    return path

async def main():
    """Run all tests"""
    try:
        # Test chat
        await test_agent_chat()
        
        # Test learning path
        await test_learning_path()
        
        print("=" * 60)
        print("✓ All tests completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("\n🚀 SkillLens AI Agent Test Suite\n")
    asyncio.run(main())
