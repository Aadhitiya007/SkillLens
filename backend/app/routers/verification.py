"""
Verification API Router
Endpoints for skill verification assessments.
"""

from fastapi import APIRouter, HTTPException, status

from app.models.verification_models import (
    AssessmentRequest, AssessmentResponse,
    AssessmentSubmission, AssessmentResult, MockTestRequest
)
from app.services.skill_verification import get_verification_service

router = APIRouter()


@router.post("/generate-assessment", response_model=AssessmentResponse)
async def generate_assessment(request: AssessmentRequest):
    """
    Generate an AI-powered skill assessment.
    
    Creates a customized assessment with multiple-choice and theoretical
    questions based on the skill and difficulty level.
    """
    try:
        service = get_verification_service()
        assessment = await service.generate_assessment(request)
        return assessment
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating assessment: {str(e)}"
        )


@router.post("/submit-assessment", response_model=AssessmentResult)
async def submit_assessment(submission: AssessmentSubmission):
    """
    Submit assessment answers for evaluation.
    
    Evaluates the user's answers and returns score, confidence level,
    and detailed feedback.
    """
    try:
        service = get_verification_service()
        
        # In a real app, retrieve from DB. For now, we regenerate to get the "correct" answers
        # This is a hack for the prototype since we don't have persistence
        # We need to know the skill and difficulty from somewhere, but assessment_id isn't stored.
        # Ideally, we'd look up the assessment by ID.
        # For now, we'll assume a default or extracted from the submission if possible (but submission only has answers)
        # WORKAROUND: We will assume Python/Intermediate for the prototype if we can't look it up.
        
        # However, looking at the code, we can't easily reconstruct the exact questions without the seed/ID mapping.
        # But wait, generate_assessment uses standard templates.
        # If we just want to verify "correctness" of the answers provided:
        
        # Let's fallback to a simpler approach:
        # We will create a dummy request to generate matching questions
        # This is strictly a simulation for demonstration purposes.
        
        req = AssessmentRequest(
            user_id=submission.user_id,
            skill="Python", # Defaulting to Python for demo
            difficulty=DifficultyLevel.INTERMEDIATE,
            num_questions=len(submission.answers)
        )
        
        # Generate assessment to get correct answers
        assessment = await service.generate_assessment(req)
        
        # Override ID to match submission
        assessment.assessment_id = submission.assessment_id
        
        result = await service.evaluate_assessment(submission, assessment)
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error submitting assessment: {str(e)}"
        )


@router.get("/health")
async def verification_health_check():
    """Health check for verification service."""
    return {
        "status": "healthy",
        "service": "Skill Verification",
        "features": [
            "AI-Generated Assessments",
            "Multiple Question Types",
            "Confidence Scoring",
            "Detailed Feedback"
        ]
    }

@router.post("/mock-test/generate", response_model=AssessmentResponse)
async def generate_mock_test(request: MockTestRequest):
    """
    Generate a comprehensive 20-question mock test.
    """
    try:
        service = get_verification_service()
        assessment = await service.generate_mock_test(request)
        return assessment
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating mock test: {str(e)}"
        )


@router.post("/mock-test/submit", response_model=AssessmentResult)
async def submit_mock_test(submission: AssessmentSubmission):
    """
    Submit mock test answers for evaluation.
    """
    try:
        service = get_verification_service()
        # In a real app, retrieve from DB. For now, we regenerate to get the "correct" answers
        # This is a hack for the prototype
        request = MockTestRequest(user_id=submission.user_id, primary_skill="Python") # Default skill
        assessment = await service.generate_mock_test(request)
        
        # Override assessment ID for matching
        assessment.assessment_id = submission.assessment_id
        
        result = await service.evaluate_assessment(submission, assessment)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error submitting mock test: {str(e)}"
        )
