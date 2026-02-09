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
    AssessmentSubmission, AssessmentResult,
    MockTestRequest
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
                    },
                    {
                        "question": "What is the correct file extension for Python files?",
                        "options": [".pyth", ".pt", ".py", ".pe"],
                        "answer": ".py",
                        "explanation": "Python source files use the .py extension."
                    },
                    {
                        "question": "How do you insert comments in Python code?",
                        "options": ["//", "#", "/* */", "--"],
                        "answer": "#",
                        "explanation": "Python uses the # symbol for single-line comments."
                    },
                    {
                        "question": "Which of these is NOT a core data type in Python?",
                        "options": ["List", "Dictionary", "Tuple", "Class"],
                        "answer": "Class",
                        "explanation": "Class is a blueprint for objects, not a primitive/core data type like List or Tuple."
                    },
                    {
                        "question": "What is the output of: 3 ** 2?",
                        "options": ["6", "9", "5", "8"],
                        "answer": "9",
                        "explanation": "** is the exponentiation operator (3 to the power of 2)."
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
                    },
                    {
                        "question": "What is the purpose of the 'self' keyword?",
                        "options": ["It refers to the class itself", "It refers to the instance of the class", "It is a reserved keyword for import", "It makes a variable global"],
                        "answer": "It refers to the instance of the class",
                        "explanation": "self represents the instance of the class and binds attributes with the given arguments."
                    },
                    {
                        "question": "Which collection type is immutable?",
                        "options": ["List", "Set", "Dictionary", "Tuple"],
                        "answer": "Tuple",
                        "explanation": "Tuples are immutable sequences, unlike lists or dictionaries."
                    },
                    {
                        "question": "What does the *args parameter do?",
                        "options": ["Passes keyword arguments", "Passes a variable number of non-keyword arguments", "Multiplies arguments", "Imports arguments"],
                        "answer": "Passes a variable number of non-keyword arguments",
                        "explanation": "*args allows you to pass a variable number of positional arguments to a function."
                    },
                    {
                        "question": "How do you handle exceptions in Python?",
                        "options": ["try-except", "do-catch", "try-catch", "catch-throw"],
                        "answer": "try-except",
                        "explanation": "Python uses try and except blocks to handle errors and exceptions."
                    },
                    {
                        "question": "What is a decorator?",
                        "options": ["A function that modifies the behavior of another function", "A design pattern for classes", "A UI component", "A variable type"],
                        "answer": "A function that modifies the behavior of another function",
                        "explanation": "Decorators allow you to wrap another function in order to extend the behavior of the wrapped function."
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
                    },
                    {
                        "question": "What is the Global Interpreter Lock (GIL)?",
                        "options": ["A lock that prevents multiple threads from executing bytecodes at once", "A security feature", "A database lock", "A module importer"],
                        "answer": "A lock that prevents multiple threads from executing bytecodes at once",
                        "explanation": "The GIL is a mutex that protects access to Python objects, preventing multiple threads from executing Python bytecodes at once."
                    },
                    {
                        "question": "What is a generator in Python?",
                        "options": ["A function that returns an iterator using 'yield'", "A tool to create lists", "A random number generator", "A compiler"],
                        "answer": "A function that returns an iterator using 'yield'",
                        "explanation": "Generators are functions that return an iterator and yield a sequence of values one at a time."
                    },
                    {
                        "question": "What is the result of using 'is' vs '=='?",
                        "options": ["'is' checks identity, '==' checks equality", "'is' checks equality, '==' checks identity", "They are identical", "'is' is deprecated"],
                        "answer": "'is' checks identity, '==' checks equality",
                        "explanation": "'is' checks if two variables point to the same object in memory, '==' checks if their values are equal."
                    },
                    {
                        "question": "What is correct about Python's memory management?",
                        "options": ["It uses manual memory management", "It uses private heap space and garbage collection", "It relies solely on OS", "It has no memory management"],
                        "answer": "It uses private heap space and garbage collection",
                        "explanation": "Python memory management involves a private heap containing all Python objects and data structures, managed by the Python memory manager."
                    },
                    {
                        "question": "What are metaclasses?",
                        "options": ["Classes of classes", "Special methods", "Abstract base classes", "Imported modules"],
                        "answer": "Classes of classes",
                        "explanation": "A metaclass is a class whose instances are classes. It defines how a class behaves."
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
            },
            "Aptitude": [
                {
                    "question": "What is the next number in the series: 2, 4, 8, 16, ...?",
                    "options": ["30", "32", "34", "36"],
                    "answer": "32",
                    "explanation": "The series doubles each time."
                },
                {
                    "question": "If a shirt costs $20 after a 20% discount, what was the original price?",
                    "options": ["$22", "$24", "$25", "$30"],
                    "answer": "$25",
                    "explanation": "x * 0.8 = 20 => x = 20 / 0.8 = 25"
                },
                {
                    "question": "Train A runs at 60km/h, Train B at 40km/h. How far apart are they after 2 hours if strictly moving away?",
                    "options": ["100km", "200km", "150km", "50km"],
                    "answer": "200km",
                    "explanation": "(60 + 40) * 2 = 200km"
                },
                {
                    "question": "Which word is the odd one out?",
                    "options": ["Apple", "Banana", "Carrot", "Grape"],
                    "answer": "Carrot",
                    "explanation": "Carrot is a vegetable, others are fruits."
                },
                {
                    "question": "Complete the series: 3, 5, 9, 17, ...",
                    "options": ["25", "33", "35", "41"],
                    "answer": "33",
                    "explanation": "Difference doubles: +2, +4, +8, +16. 17+16=33."
                },
                {
                    "question": "If P is the brother of Q, and Q is the sister of R, how is P related to R?",
                    "options": ["Brother", "Sister", "Father", "Cousin"],
                    "answer": "Brother",
                    "explanation": "P is male (brother), so P is R's brother."
                }
            ]
        }
    


    async def generate_assessment(self, request: AssessmentRequest) -> AssessmentResponse:
        """
        Generate a skill assessment based on request.
        """
        try:
            assessment_id = str(uuid.uuid4())
            
            # Get templates for the skill
            skill_templates = self.question_templates.get(
                request.skill,
                self.question_templates.get("Python") # Fallback to Python if skill not found
            )
            
            # Get questions based on difficulty
            questions = self._get_questions(
                skill_templates, 
                request.difficulty, 
                request.num_questions, 
                request.skill, 
                assessment_id, 
                0
            )
            
            total_points = sum(q.points for q in questions)
            
            return AssessmentResponse(
                assessment_id=assessment_id,
                skill=request.skill,
                questions=questions,
                total_points=total_points,
                time_limit_minutes=15 # 15 mins for standard assessment
            )
            
        except Exception as e:
            logger.error(f"Error generating assessment: {e}")
            raise


    async def generate_mock_test(self, request: MockTestRequest) -> AssessmentResponse:
        """
        Generate a comprehensive 20-question mock test + 5 coding challenges.
        Structure:
        - 5 Easy (Skill)
        - 5 Intermediate (Skill)
        - 5 Hard (Skill)
        - 5 Aptitude (General)
        - 5 Coding Challenges (JS, Python, General, HTML, CSS)
        """
        try:
            assessment_id = str(uuid.uuid4())
            
            # Try to generate with AI first (MCQs only)
            if settings.openai_api_key:
                try:
                    return await self._generate_with_ai(request, assessment_id)
                except Exception as e:
                    logger.error(f"AI generation failed, falling back to templates: {e}")
                    # Fallthrough to template logic below
            
            questions = []
            
            # Get templates
            skill_templates = self.question_templates.get(
                request.primary_skill,
                self.question_templates.get("Python")
            )
            
            # 1. 5 Easy Questions
            easy_qs = self._get_questions(skill_templates, DifficultyLevel.BEGINNER, 5, request.primary_skill, assessment_id, 0)
            questions.extend(easy_qs)
            
            # 2. 5 Intermediate Questions
            med_qs = self._get_questions(skill_templates, DifficultyLevel.INTERMEDIATE, 5, request.primary_skill, assessment_id, 5)
            questions.extend(med_qs)

            # 3. 5 Hard Questions
            hard_qs = self._get_questions(skill_templates, DifficultyLevel.ADVANCED, 5, request.primary_skill, assessment_id, 10)
            questions.extend(hard_qs)
            
            # 4. 5 Aptitude Questions
            aptitude_pool = self.question_templates.get("Aptitude", [])
            import random
            selected_aptitude = random.sample(aptitude_pool, min(5, len(aptitude_pool)))
            
            for i, tmpl in enumerate(selected_aptitude):
                questions.append(Question(
                    question_id=f"{assessment_id}-apt{i+1}",
                    skill="Aptitude",
                    question_text=tmpl["question"],
                    question_type=QuestionType.APTITUDE,
                    difficulty=DifficultyLevel.INTERMEDIATE,
                    options=tmpl.get("options", []),
                    correct_answer=tmpl["answer"],
                    explanation=tmpl["explanation"],
                    points=5
                ))
                
            # 5. 5 Coding Challenges (Shared Logic)
            coding_qs = self._get_coding_challenges(assessment_id, request.primary_skill)
            questions.extend(coding_qs)
            
            total_points = sum(q.points for q in questions)
            
            return AssessmentResponse(
                assessment_id=assessment_id,
                skill=request.primary_skill,
                questions=questions,
                total_points=total_points,
                time_limit_minutes=60 # Increased time for coding
            )
            
        except Exception as e:
            logger.error(f"Error generating mock test: {e}")
            raise

    async def _generate_with_ai(self, request: MockTestRequest, assessment_id: str) -> AssessmentResponse:
        """Generate test using OpenAI."""
        from openai import AsyncOpenAI
        import json
        
        client = AsyncOpenAI(api_key=settings.openai_api_key)
        
        prompt = f"""
        Generate a technical skill assessment for {request.primary_skill}.
        Return a JSON object with a list of 'questions'.
        
        Structure the test with exactly:
        - 5 Beginner questions (Multiple Choice)
        - 5 Intermediate questions (Multiple Choice)
        - 5 Advanced questions (Multiple Choice)
        - 5 Aptitude/Logic questions (Multiple Choice)
        
        Do NOT generate coding questions.
        
        Format for each question:
        {{
            "question_text": "...",
            "options": ["A", "B", "C", "D"],
            "correct_answer": "...",
            "explanation": "...",
            "difficulty": "beginner"|"intermediate"|"advanced",
            "type": "multiple_choice"|"aptitude",
            "points": 10
        }}
        """
        
        response = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a senior technical interviewer. Generate valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            response_format={"type": "json_object"}
        )
        
        content = response.choices[0].message.content
        data = json.loads(content)
        
        questions = []
        raw_qs = data.get("questions", [])
        
        for i, q in enumerate(raw_qs):
            q_type = QuestionType.MULTIPLE_CHOICE
            if q.get("type") == "aptitude":
                q_type = QuestionType.APTITUDE
                
            q_diff = DifficultyLevel.INTERMEDIATE
            if q.get("difficulty") == "beginner":
                q_diff = DifficultyLevel.BEGINNER
            elif q.get("difficulty") == "advanced":
                q_diff = DifficultyLevel.ADVANCED
                
            questions.append(Question(
                question_id=f"{assessment_id}-q{i+1}",
                skill=request.primary_skill if q_type != QuestionType.APTITUDE else "Aptitude",
                question_text=q["question_text"],
                question_type=q_type,
                difficulty=q_diff,
                options=q.get("options"),
                correct_answer=q["correct_answer"],
                explanation=q["explanation"],
                points=q.get("points", 10 if q_type != QuestionType.APTITUDE else 5),
                code_template=None
            ))
            
        # Add 5 Standard Coding Challenges
        coding_qs = self._get_coding_challenges(assessment_id, request.primary_skill)
        questions.extend(coding_qs)
            
        total_points = sum(q.points for q in questions)
        
        return AssessmentResponse(
            assessment_id=assessment_id,
            skill=request.primary_skill,
            questions=questions,
            total_points=total_points,
            time_limit_minutes=60
        )

    def _get_coding_challenges(self, assessment_id: str, primary_skill: str) -> List[Question]:
        """Generate the standard 5-section coding challenge."""
        challenges = []
        
        # 1. JavaScript Medium
        challenges.append(Question(
            question_id=f"{assessment_id}-code-js",
            skill="JavaScript",
            question_text="JavaScript (Medium): Write a function 'flattenArray' that takes a nested array and returns a flat array along with its depth.",
            question_type=QuestionType.CODING,
            difficulty=DifficultyLevel.INTERMEDIATE,
            correct_answer="N/A",
            explanation="Requires recursion or stack-based flattening.",
            points=20,
            code_template="function flattenArray(arr) {\n    // Write your code here\n}"
        ))
        
        # 2. Python
        challenges.append(Question(
            question_id=f"{assessment_id}-code-py",
            skill="Python",
            question_text="Python: Write a function 'process_data' that takes a list of dictionaries and returns a summary statistic (e.g., average age).",
            question_type=QuestionType.CODING,
            difficulty=DifficultyLevel.INTERMEDIATE,
            correct_answer="N/A",
            explanation="Requires list processing and aggregation.",
            points=20,
            code_template="def process_data(data):\n    # Write your code here\n    pass"
        ))
        
        # 3. Preferred Language / General Algo
        challenges.append(Question(
            question_id=f"{assessment_id}-code-algo",
            skill=primary_skill, # User's primary skill or General
            question_text=f"Algorithmic Challenge (Preferred Language): Implement a Binary Search algorithm to find a target in a sorted array.",
            question_type=QuestionType.CODING,
            difficulty=DifficultyLevel.ADVANCED,
            correct_answer="N/A",
            explanation="Standard O(log n) search algorithm.",
            points=30,
            code_template="# Write your solution in your preferred language\n# Binary Search Implementation"
        ))
        
        # 4. HTML
        challenges.append(Question(
            question_id=f"{assessment_id}-code-html",
            skill="HTML",
            question_text="HTML: Create a semantic HTML5 structure for a Blog Post containing a header, main article, and footer.",
            question_type=QuestionType.CODING,
            difficulty=DifficultyLevel.BEGINNER,
            correct_answer="N/A",
            explanation="Semantic tags like <article>, <header>, <footer>.",
            points=15,
            code_template="<!-- Write your HTML structure here -->\n"
        ))
        
        # 5. CSS Medium
        challenges.append(Question(
            question_id=f"{assessment_id}-code-css",
            skill="CSS",
            question_text="CSS (Medium): Create a Flexbox layout where 3 items are evenly spaced and centered vertically in a container.",
            question_type=QuestionType.CODING,
            difficulty=DifficultyLevel.INTERMEDIATE,
            correct_answer="N/A",
            explanation="Use display: flex, justify-content: space-between, align-items: center.",
            points=15,
            code_template=".container {\n    /* Write your CSS here */\n}\n\n.item {\n    \n}"
        ))
        
        return challenges

    def _get_questions(self, templates, difficulty, count, skill, aid, offset):
        qs = []
        subset = templates.get(difficulty.value, [])
        
        # If no templates for this difficulty/skill, try to populate from other difficulties if possible
        # or fall back to generic but clean format
        if not subset:
            # Fallback for genuinely missing content: generic coding questions better than "Option A"
            for i in range(count):
                qs.append(Question(
                    question_id=f"{aid}-q{offset+i+1}",
                    skill=skill,
                    question_text=f"Concept check: Explain the core principles of {skill} related to {difficulty.value} concepts.",
                    question_type=QuestionType.MULTIPLE_CHOICE,
                    difficulty=difficulty,
                    options=[f"{skill} Principle A", f"{skill} Principle B", f"{skill} Principle C", "All of the above"],
                    correct_answer="All of the above",
                    explanation="Understanding core principles is key.",
                    points=10
                ))
            return qs

        import random
        # Randomly select questions. If we need more than we have, we allow duplicates (or could strictly limit)
        # For better UX, we try to be unique first.
        
        available = list(subset)
        selected_templates = []
        
        if count <= len(available):
            selected_templates = random.sample(available, count)
        else:
            # We need more than we have. Take all, then random sample for remainder
            selected_templates.extend(available)
            for _ in range(count - len(available)):
                selected_templates.append(random.choice(available))
                
        for i, tmpl in enumerate(selected_templates):
            qs.append(Question(
                question_id=f"{aid}-q{offset+i+1}",
                skill=skill,
                question_text=tmpl["question"],
                question_type=QuestionType.MULTIPLE_CHOICE,
                difficulty=difficulty,
                options=tmpl["options"],
                correct_answer=tmpl["answer"],
                explanation=tmpl["explanation"],
                points=10 if difficulty == DifficultyLevel.BEGINNER else (20 if difficulty == DifficultyLevel.INTERMEDIATE else 30)
            ))
            
        return qs

    async def evaluate_assessment(self, submission: AssessmentSubmission, 
                                  assessment: AssessmentResponse) -> AssessmentResult:
        """
        Evaluate user's assessment submission.
        """
        try:
            score = 0
            max_score = assessment.total_points
            feedback = []
            recommendations = []
            
            # Create answer map
            answer_map = {ans.question_id: ans.user_answer for ans in submission.answers}
            
            # Evaluate each question
            for question in assessment.questions:
                user_answer = answer_map.get(question.question_id, "")
                
                if question.question_type == QuestionType.CODING:
                    # Basic check for non-empty code
                    if len(user_answer.strip()) > 20:
                        score += question.points
                        feedback.append(f"✓ Coding Task: Submitted (AI Review Pending)")
                    else:
                        feedback.append(f"✗ Coding Task: Incomplete")
                        recommendations.append(f"Practice coding problems for {question.skill}")
                else:
                    if user_answer.strip().lower() == question.correct_answer.strip().lower():
                        score += question.points
                        feedback.append(f"✓ Question {question.question_id}: Correct!")
                    else:
                        feedback.append(
                            f"✗ Question {question.question_id}: Incorrect. "
                            f"Correct answer: {question.correct_answer}. "
                            f"Explanation: {question.explanation}"
                        )
                        if question.difficulty == DifficultyLevel.BEGINNER:
                            recommendations.append(f"Review basics of {question.skill}")
            
            percentage = (score / max_score * 100) if max_score > 0 else 0
            
            # Determine confidence level
            if percentage >= 80:
                confidence = "Excellent"
                passed = True
            elif percentage >= 60:
                confidence = "Good"
                passed = True
            else:
                confidence = "Needs Improvement"
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
                feedback=feedback,
                recommendations=list(set(recommendations))
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
