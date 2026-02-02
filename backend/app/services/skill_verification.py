"""
Skill Verification Service
Generates AI-powered assessments to verify user skills.
"""

import logging
from typing import List, Dict
import uuid
from datetime import datetime

from app.config import settings
from app.models.verification_models import (
    Question, QuestionType, DifficultyLevel,
    AssessmentRequest, AssessmentResponse,
    AssessmentSubmission, AssessmentResult
)

logger = logging.getLogger(__name__)


class SkillVerificationService:
    """
    AI-powered skill verification through generated assessments.
    """
    
    def __init__(self):
        """Initialize verification service."""
        # Question templates by skill
        self.question_templates = self._load_question_templates()
    
    def _load_question_templates(self) -> Dict:
        """Load question templates for different skills."""
        return {
            "Python": {
                "beginner": [
                    {
                        "question": "What is the output of: print(type([]))?",
                        "options": ["<class 'list'>", "<class 'dict'>", "<class 'tuple'>", "<class 'set'>"],
                        "answer": "<class 'list'>",
                        "explanation": "[] creates an empty list, and type() returns the class type."
                    },
                    {
                        "question": "Which keyword is used to define a function in Python?",
                        "options": ["function", "def", "func", "define"],
                        "answer": "def",
                        "explanation": "The 'def' keyword is used to define functions in Python."
                    }
                ],
                "intermediate": [
                    {
                        "question": "What is a list comprehension in Python?",
                        "options": [
                            "A way to create lists using a compact syntax",
                            "A method to compress lists",
                            "A function to understand lists",
                            "A debugging tool"
                        ],
                        "answer": "A way to create lists using a compact syntax",
                        "explanation": "List comprehensions provide a concise way to create lists based on existing lists."
                    }
                ],
                "advanced": [
                    {
                        "question": "What is the difference between __str__ and __repr__?",
                        "options": [
                            "__str__ is for end users, __repr__ is for developers",
                            "They are the same",
                            "__str__ is faster",
                            "__repr__ is deprecated"
                        ],
                        "answer": "__str__ is for end users, __repr__ is for developers",
                        "explanation": "__str__ returns a readable string, __repr__ returns an unambiguous representation."
                    }
                ]
            },
            "JavaScript": {
                "beginner": [
                    {
                        "question": "What does 'let' keyword do in JavaScript?",
                        "options": [
                            "Declares a block-scoped variable",
                            "Declares a constant",
                            "Declares a global variable",
                            "Imports a module"
                        ],
                        "answer": "Declares a block-scoped variable",
                        "explanation": "'let' declares a block-scoped local variable."
                    }
                ],
                "intermediate": [
                    {
                        "question": "What is a closure in JavaScript?",
                        "options": [
                            "A function with access to outer scope",
                            "A way to close files",
                            "An error handling mechanism",
                            "A loop terminator"
                        ],
                        "answer": "A function with access to outer scope",
                        "explanation": "A closure gives you access to an outer function's scope from an inner function."
                    }
                ],
                "advanced": [
                    {
                        "question": "What is the event loop in JavaScript?",
                        "options": [
                            "Mechanism for handling async operations",
                            "A for loop variant",
                            "An event listener",
                            "A debugging tool"
                        ],
                        "answer": "Mechanism for handling async operations",
                        "explanation": "The event loop handles asynchronous callbacks in JavaScript."
                    }
                ]
            },
            "React": {
                "beginner": [
                    {
                        "question": "What is JSX in React?",
                        "options": [
                            "JavaScript XML syntax extension",
                            "A CSS framework",
                            "A testing library",
                            "A state management tool"
                        ],
                        "answer": "JavaScript XML syntax extension",
                        "explanation": "JSX is a syntax extension that allows writing HTML-like code in JavaScript."
                    }
                ],
                "intermediate": [
                    {
                        "question": "What is the purpose of useEffect hook?",
                        "options": [
                            "Handle side effects in functional components",
                            "Create state variables",
                            "Define component props",
                            "Style components"
                        ],
                        "answer": "Handle side effects in functional components",
                        "explanation": "useEffect is used for side effects like data fetching, subscriptions, etc."
                    }
                ],
                "advanced": [
                    {
                        "question": "What is React reconciliation?",
                        "options": [
                            "Process of updating the DOM efficiently",
                            "A state management pattern",
                            "A routing mechanism",
                            "A testing strategy"
                        ],
                        "answer": "Process of updating the DOM efficiently",
                        "explanation": "Reconciliation is React's algorithm for efficiently updating the DOM."
                    }
                ]
            }
        }
    
    async def generate_assessment(self, request: AssessmentRequest) -> AssessmentResponse:
        """
        Generate an AI-powered assessment for a skill.
        
        Args:
            request: Assessment request with skill and difficulty
            
        Returns:
            Generated assessment with questions
        """
        try:
            assessment_id = str(uuid.uuid4())
            questions = []
            
            # Get question templates for skill
            skill_templates = self.question_templates.get(
                request.skill,
                self.question_templates.get("Python")  # Default fallback
            )
            
            difficulty_templates = skill_templates.get(request.difficulty.value, [])
            
            # Generate questions
            for idx, template in enumerate(difficulty_templates[:request.num_questions]):
                question = Question(
                    question_id=f"{assessment_id}-q{idx+1}",
                    skill=request.skill,
                    question_text=template["question"],
                    question_type=QuestionType.MULTIPLE_CHOICE,
                    difficulty=request.difficulty,
                    options=template["options"],
                    correct_answer=template["answer"],
                    explanation=template["explanation"],
                    points=10
                )
                questions.append(question)
            
            # If not enough templates, generate generic questions
            while len(questions) < request.num_questions:
                questions.append(Question(
                    question_id=f"{assessment_id}-q{len(questions)+1}",
                    skill=request.skill,
                    question_text=f"What is an important concept in {request.skill}?",
                    question_type=QuestionType.THEORETICAL,
                    difficulty=request.difficulty,
                    correct_answer="Varies",
                    explanation="This is a theoretical question.",
                    points=10
                ))
            
            total_points = sum(q.points for q in questions)
            time_limit = len(questions) * 3  # 3 minutes per question
            
            return AssessmentResponse(
                assessment_id=assessment_id,
                skill=request.skill,
                questions=questions,
                total_points=total_points,
                time_limit_minutes=time_limit
            )
            
        except Exception as e:
            logger.error(f"Error generating assessment: {e}")
            raise
    
    async def evaluate_assessment(self, submission: AssessmentSubmission, 
                                  assessment: AssessmentResponse) -> AssessmentResult:
        """
        Evaluate user's assessment submission.
        
        Args:
            submission: User's answers
            assessment: Original assessment
            
        Returns:
            Assessment results with score and feedback
        """
        try:
            score = 0
            max_score = assessment.total_points
            feedback = []
            
            # Create answer map
            answer_map = {ans.question_id: ans.user_answer for ans in submission.answers}
            
            # Evaluate each question
            for question in assessment.questions:
                user_answer = answer_map.get(question.question_id, "")
                
                if user_answer.strip().lower() == question.correct_answer.strip().lower():
                    score += question.points
                    feedback.append(f"✓ Question {question.question_id}: Correct!")
                else:
                    feedback.append(
                        f"✗ Question {question.question_id}: Incorrect. "
                        f"Correct answer: {question.correct_answer}. "
                        f"Explanation: {question.explanation}"
                    )
            
            percentage = (score / max_score * 100) if max_score > 0 else 0
            
            # Determine confidence level
            if percentage >= 80:
                confidence = "Verified"
                passed = True
            elif percentage >= 60:
                confidence = "Partial"
                passed = True
            else:
                confidence = "Not Verified"
                passed = False
            
            return AssessmentResult(
                assessment_id=submission.assessment_id,
                user_id=submission.user_id,
                skill=assessment.skill,
                score=score,
                max_score=max_score,
                percentage=round(percentage, 1),
                confidence_level=confidence,
                passed=passed,
                feedback=feedback
            )
            
        except Exception as e:
            logger.error(f"Error evaluating assessment: {e}")
            raise


# Singleton instance
_verification_service = None

def get_verification_service() -> SkillVerificationService:
    """Get singleton instance of verification service."""
    global _verification_service
    if _verification_service is None:
        _verification_service = SkillVerificationService()
    return _verification_service
