'use client';

import { useState } from 'react';
import { ArrowRight, CheckCircle, Clock, Code, Award, Brain, Target, BookOpen } from 'lucide-react';
import Link from 'next/link';

// Types
type QuestionType = 'multiple_choice' | 'code' | 'theoretical' | 'coding' | 'aptitude';
type Difficulty = 'beginner' | 'intermediate' | 'advanced';

interface Question {
    question_id: string;
    skill: string;
    question_text: string;
    question_type: QuestionType;
    difficulty: Difficulty;
    options?: string[];
    points: number;
    code_template?: string;
}

interface AssessmentResponse {
    assessment_id: string;
    skill: string;
    questions: Question[];
    total_points: number;
    time_limit_minutes: number;
}

interface AssessmentResult {
    score: number;
    max_score: number;
    percentage: number;
    confidence_level: string;
    passed: boolean;
    feedback: string[];
    recommendations: string[];
}

export default function MockTestPage() {
    const [started, setStarted] = useState(false);
    const [loading, setLoading] = useState(false);
    const [assessment, setAssessment] = useState<AssessmentResponse | null>(null);
    const [currentStep, setCurrentStep] = useState(0); // 0-4: Sections
    const [answers, setAnswers] = useState<Record<string, string>>({});
    const [result, setResult] = useState<AssessmentResult | null>(null);


    const startTest = async () => {
        setLoading(true);
        try {
            // Hardcoded skill for prototype, ideally comes from user profile
            const response = await fetch('http://localhost:8000/api/verification/mock-test/generate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ user_id: 'test-user', primary_skill: 'Python' })
            });

            if (!response.ok) {
                throw new Error('Failed to generate test. Please ensure backend is running.');
            }

            const data = await response.json();

            if (!data.questions || !Array.isArray(data.questions)) {
                throw new Error('Invalid test data received');
            }

            setAssessment(data);
            setStarted(true);
        } catch (error) {
            console.error('Failed to start test:', error);
            alert('Failed to start test. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    const submitTest = async () => {
        if (!assessment) return;
        setLoading(true);
        try {
            const submission = {
                assessment_id: assessment.assessment_id,
                user_id: 'test-user',
                answers: Object.entries(answers).map(([qid, ans]) => ({
                    question_id: qid,
                    user_answer: ans
                }))
            };

            const response = await fetch('http://localhost:8000/api/verification/mock-test/submit', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(submission)
            });

            if (!response.ok) {
                throw new Error('Failed to submit test');
            }

            const data = await response.json();
            setResult(data);
        } catch (error) {
            console.error('Failed to submit test:', error);
            alert('Error submitting test. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    const currentQuestions = assessment?.questions ? assessment.questions.slice(currentStep * 5, (currentStep + 1) * 5) : [];
    const isLastStep = currentStep === 4; // 5 steps total (Easy, Med, Hard, Aptitude, Coding)

    // Group questions by section name for display
    const getSectionName = (step: number) => {
        switch (step) {
            case 0: return "Section 1: Basic Concept Check (Easy)";
            case 1: return "Section 2: Intermediate Concepts";
            case 2: return "Section 3: Advanced Challenges";
            case 3: return "Section 4: Aptitude & Logic";
            case 4: return "Section 5: Coding Challenge";
            default: return "";
        }
    };

    if (result) {
        return (
            <div className="min-h-screen bg-slate-50 dark:bg-slate-900 py-12 px-6">
                <div className="max-w-4xl mx-auto space-y-8">
                    <div className="text-center space-y-4">
                        <div className="inline-flex p-4 rounded-full bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 mb-2">
                            <Award className="w-12 h-12" />
                        </div>
                        <h1 className="text-3xl font-bold text-slate-900 dark:text-white">Assessment Complete!</h1>
                        <p className="text-slate-600 dark:text-slate-400">Here is your detailed performance analysis.</p>
                    </div>

                    {/* Score Card */}
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                        <div className="bg-white dark:bg-slate-800 p-6 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700 text-center">
                            <div className="text-sm text-slate-500 mb-1">Overall Score</div>
                            <div className="text-4xl font-bold text-blue-600 dark:text-blue-400">{result.score}/{result.max_score}</div>
                            <div className={`text-sm font-medium mt-2 ${result.passed ? 'text-green-500' : 'text-orange-500'}`}>
                                {result.passed ? 'PASSED' : 'NEEDS IMPROVEMENT'}
                            </div>
                        </div>
                        <div className="bg-white dark:bg-slate-800 p-6 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700 text-center">
                            <div className="text-sm text-slate-500 mb-1">Proficiency Level</div>
                            <div className="text-2xl font-bold text-purple-600 dark:text-purple-400 mt-2">{result.confidence_level}</div>
                        </div>
                        <div className="bg-white dark:bg-slate-800 p-6 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700 text-center">
                            <div className="text-sm text-slate-500 mb-1">Percentage</div>
                            <div className="text-4xl font-bold text-slate-900 dark:text-white">{result.percentage}%</div>
                        </div>
                    </div>

                    {/* AI Feedback */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                        <div className="bg-white dark:bg-slate-800 p-6 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700">
                            <h3 className="text-lg font-bold text-slate-900 dark:text-white mb-4 flex items-center gap-2">
                                <Target className="w-5 h-5 text-red-500" />
                                Areas for Improvement
                            </h3>
                            <ul className="space-y-3">
                                {result.feedback.filter(f => f.startsWith('✗')).slice(0, 5).map((item, i) => (
                                    <li key={i} className="text-sm text-slate-600 dark:text-slate-400 bg-red-50 dark:bg-red-900/10 p-3 rounded-lg border border-red-100 dark:border-red-900/20">
                                        {item.replace('✗ ', '')}
                                    </li>
                                ))}
                                {result.feedback.filter(f => f.startsWith('✗')).length === 0 && (
                                    <p className="text-sm text-slate-500 italic">No major weak spots identified. Great job!</p>
                                )}
                            </ul>
                        </div>

                        <div className="bg-white dark:bg-slate-800 p-6 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700">
                            <h3 className="text-lg font-bold text-slate-900 dark:text-white mb-4 flex items-center gap-2">
                                <Brain className="w-5 h-5 text-blue-500" />
                                AI Coach Recommendations
                            </h3>
                            <div className="space-y-3">
                                {result.recommendations.length > 0 ? (
                                    result.recommendations.map((rec, i) => (
                                        <div key={i} className="flex items-start gap-3 p-3 bg-blue-50 dark:bg-blue-900/10 rounded-lg border border-blue-100 dark:border-blue-900/20">
                                            <BookOpen className="w-4 h-4 text-blue-500 shrink-0 mt-0.5" />
                                            <span className="text-sm text-slate-700 dark:text-slate-300">{rec}</span>
                                        </div>
                                    ))
                                ) : (
                                    <p className="text-sm text-slate-500 italic">Keep up the good work! Try advanced projects next.</p>
                                )}
                            </div>
                        </div>
                    </div>

                    <div className="text-center pt-8">
                        <Link href="/dashboard" className="px-8 py-3 bg-slate-900 dark:bg-white text-white dark:text-slate-900 rounded-lg font-semibold hover:opacity-90 transition-opacity">
                            Return to Dashboard
                        </Link>
                    </div>
                </div>
            </div>
        );
    }

    if (!started) {
        return (
            <div className="min-h-screen bg-slate-50 dark:bg-slate-900 flex items-center justify-center p-6">
                <div className="max-w-md w-full bg-white dark:bg-slate-800 p-8 rounded-2xl shadow-xl border border-slate-200 dark:border-slate-700 text-center">
                    <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-purple-600 rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-lg transform rotate-3">
                        <Brain className="w-8 h-8 text-white" />
                    </div>
                    <h1 className="text-2xl font-bold text-slate-900 dark:text-white mb-2">SkillLens Mock Test</h1>
                    <p className="text-slate-600 dark:text-slate-400 mb-8">
                        Ready to test your skills? This mock test consists of 20 Technical & Aptitude questions plus a Coding Challenge.
                    </p>

                    <div className="space-y-4 mb-8 text-left bg-slate-50 dark:bg-slate-900/50 p-4 rounded-xl">
                        <div className="flex items-center gap-3 text-sm text-slate-700 dark:text-slate-300">
                            <CheckCircle className="w-4 h-4 text-green-500" />
                            <span>15 Technical MCQs (Easy to Hard)</span>
                        </div>
                        <div className="flex items-center gap-3 text-sm text-slate-700 dark:text-slate-300">
                            <CheckCircle className="w-4 h-4 text-green-500" />
                            <span>5 Aptitude & Logic Questions</span>
                        </div>
                        <div className="flex items-center gap-3 text-sm text-slate-700 dark:text-slate-300">
                            <Code className="w-4 h-4 text-purple-500" />
                            <span>1 Coding Challenge</span>
                        </div>
                        <div className="flex items-center gap-3 text-sm text-slate-700 dark:text-slate-300">
                            <Clock className="w-4 h-4 text-orange-500" />
                            <span>~45 Minutes Duration</span>
                        </div>
                    </div>

                    <button
                        onClick={startTest}
                        disabled={loading}
                        className="w-full px-6 py-3.5 bg-blue-600 hover:bg-blue-700 text-white rounded-xl font-bold shadow-lg shadow-blue-500/25 transition-all text-base flex items-center justify-center gap-2 group"
                    >
                        {loading ? 'Generating Test...' : (
                            <>
                                Start Test
                                <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                            </>
                        )}
                    </button>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-slate-50 dark:bg-slate-900 py-8 px-6">
            <div className="max-w-3xl mx-auto">
                <div className="mb-8 flex items-center justify-between">
                    <div>
                        <h2 className="text-xl font-bold text-slate-900 dark:text-white">{getSectionName(currentStep)}</h2>
                        <p className="text-sm text-slate-500 dark:text-slate-400">Step {currentStep + 1} of 5</p>
                    </div>
                    <div className="flex items-center gap-2 text-slate-600 dark:text-slate-400 bg-white dark:bg-slate-800 px-3 py-1.5 rounded-lg border border-slate-200 dark:border-slate-700 shadow-sm">
                        <Clock className="w-4 h-4" />
                        <span className="text-sm font-medium font-mono">45:00</span>
                    </div>
                </div>

                <div className="space-y-6">
                    {currentQuestions.map((q, idx) => (
                        <div key={q.question_id} className="bg-white dark:bg-slate-800 p-6 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700 animate-fadeIn">
                            <div className="flex items-start justify-between gap-4 mb-4">
                                <h3 className="text-base font-semibold text-slate-900 dark:text-white">
                                    <span className="text-slate-400 mr-2">Q{idx + 1 + (currentStep * 5)}.</span>
                                    {q.question_text}
                                </h3>
                                <span className="px-2 py-1 bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300 text-xs font-bold rounded uppercase tracking-wider shrink-0">
                                    {q.points} pts
                                </span>
                            </div>

                            {q.question_type === 'code' || q.question_type === 'coding' ? (
                                <div className="space-y-3">
                                    <textarea
                                        value={answers[q.question_id] || q.code_template || ''}
                                        onChange={(e) => setAnswers({ ...answers, [q.question_id]: e.target.value })}
                                        className="w-full h-48 bg-slate-900 text-slate-100 font-mono text-sm p-4 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                                        placeholder="Write your code here..."
                                    />
                                </div>
                            ) : (
                                <div className="space-y-3">
                                    {q.options?.map((opt, i) => (
                                        <label key={i} className={`flex items-center gap-3 p-4 rounded-lg border cursor-pointer transition-all ${answers[q.question_id] === opt
                                            ? 'bg-blue-50 dark:bg-blue-900/20 border-blue-500 shadow-sm'
                                            : 'border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-700/50'
                                            }`}>
                                            <input
                                                type="radio"
                                                name={q.question_id}
                                                value={opt}
                                                checked={answers[q.question_id] === opt}
                                                onChange={(e) => setAnswers({ ...answers, [q.question_id]: e.target.value })}
                                                className="w-4 h-4 text-blue-600 focus:ring-blue-500"
                                            />
                                            <span className="text-sm text-slate-700 dark:text-slate-200">{opt}</span>
                                        </label>
                                    ))}
                                </div>
                            )}
                        </div>
                    ))}
                </div>

                <div className="mt-8 flex justify-end">
                    {isLastStep ? (
                        <button
                            onClick={submitTest}
                            disabled={loading}
                            className="px-8 py-3 bg-green-600 hover:bg-green-700 text-white rounded-lg font-bold shadow-lg shadow-green-500/20 transition-all flex items-center gap-2"
                        >
                            {loading ? 'Submitting...' : 'Submit Test'}
                            <CheckCircle className="w-5 h-5" />
                        </button>
                    ) : (
                        <button
                            onClick={() => {
                                window.scrollTo({ top: 0, behavior: 'smooth' });
                                setCurrentStep(prev => prev + 1);
                            }}
                            className="px-8 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-bold shadow-lg shadow-blue-500/20 transition-all flex items-center gap-2"
                        >
                            Next Section
                            <ArrowRight className="w-5 h-5" />
                        </button>
                    )}
                </div>
            </div>
        </div>
    );
}
