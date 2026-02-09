
import asyncio
import os
import sys
from app.services.skill_verification import SkillVerificationService
from app.models.verification_models import MockTestRequest, AssessmentSubmission, AnswerSubmission, QuestionType

from typing import Optional
from app.config import settings
settings.openai_api_key = None 

async def test_grading_flow():
    print("Testing Mock Test Grading Flow (Template Mode)...")
    service = SkillVerificationService()
    
    # 1. Generate Test
    req = MockTestRequest(user_id="debug_user", primary_skill="Python")
    assessment = await service.generate_mock_test(req)
    print(f"Generated Assessment ID: {assessment.assessment_id}")
    print(f"Total Questions: {len(assessment.questions)}")
    
    # 2. Simulate User Answers (Correctly)
    answers = []
    print("\nSimulating Answers...")
    for q in assessment.questions:
        ans = ""
        if q.question_type == QuestionType.CODING:
            ans = "def solution():\n    return 'This is a valid submission with enough length'"
        else:
            ans = q.correct_answer # Cheat: provide correct answer
            
        answers.append(AnswerSubmission(
            question_id=q.question_id,
            user_answer=ans
        ))
        
    submission = AssessmentSubmission(
        assessment_id=assessment.assessment_id,
        user_id="debug_user",
        answers=answers
    )
    
    # 3. Evaluate (This uses the regeneration logic internally if we call via router, 
    # but here we call service directly. Wait, service.evaluate_assessment takes the assessment object!
    # The ROUTER is where the regeneration hack lives.
    # To test the fix, we must mimic the ROUTER's behavior: regenerate using the ID.)
    
    # Mimic Router Logic:
    print("\nRegenerating Assessment for Grading (Mimicking Router)...")
    regenerated_assessment = await service.generate_mock_test(req, assessment_id=assessment.assessment_id)
    
    # Verify IDs match
    ids_match = True
    for q1, q2 in zip(assessment.questions, regenerated_assessment.questions):
        if q1.question_id != q2.question_id:
            print(f"❌ ID Mismatch! Original: {q1.question_id}, Regen: {q2.question_id}")
            ids_match = False
        if q1.correct_answer != q2.correct_answer:
             # This assumes templates are deterministic.
             print(f"❌ Content Mismatch! {q1.question_text[:20]}... vs {q2.question_text[:20]}...")
    
    if ids_match:
        print("✅ IDs Match between Original and Regenerated Test.")
        
    # 4. Perform Grading
    result = await service.evaluate_assessment(submission, regenerated_assessment)
    
    print(f"\nGrading Result:")
    print(f"Score: {result.score} / {result.max_score}")
    print(f"Percentage: {result.percentage}%")
    print(f"Passed: {result.passed}")
    
    if result.percentage == 100.0:
        print("SUCCESS: Perfect score achieved (Grading logic works).")
    else:
        print("FAILURE: Score is not 100%. Mismatch occurred.")
        # Debug fail
        for fb in result.feedback:
            if "✗" in fb:
                print(fb)

if __name__ == "__main__":
    sys.path.append(os.getcwd())
    with open("debug_grading_out.txt", "w", encoding="utf-8") as f:
        sys.stdout = f
        asyncio.run(test_grading_flow())
