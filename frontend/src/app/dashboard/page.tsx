'use client';

import { useState, useEffect } from 'react';
import DashboardStats from '@/components/dashboard-stats';
import SkillGapChart from '@/components/skill-gap-chart';
import LearningPathView from '@/components/learning-path-view';
import ReadinessGauge from '@/components/readiness-gauge';
import { Upload, Sparkles } from 'lucide-react';
import Link from 'next/link';
import GitHubVerificationBox from '@/components/github-verification-box';

export default function DashboardPage() {
    const [dashboardData, setDashboardData] = useState({
        readinessScore: 0,
        skillsMatched: 0,
        skillsRequired: 0,
        predictedSuccessRate: 0,
        learningProgress: 0,
        matchedSkills: [] as string[],
        missingSkills: [] as string[],
        learningSkills: [] as string[],
        learningPath: [] as any[],
        targetRole: 'Full Stack Developer',
    });

    const [loading, setLoading] = useState(true);

    useEffect(() => {
        // Simulate loading data
        // TODO: Replace with actual API calls
        setTimeout(() => {
            setDashboardData({
                readinessScore: 72,
                skillsMatched: 8,
                skillsRequired: 12,
                predictedSuccessRate: 65,
                learningProgress: 45,
                matchedSkills: ['Python', 'JavaScript', 'React', 'HTML', 'CSS', 'Git', 'SQL', 'REST APIs'],
                missingSkills: ['Node.js', 'MongoDB', 'Docker', 'TypeScript'],
                learningSkills: [],
                learningPath: [
                    {
                        step_number: 1,
                        skill: 'Node.js',
                        description: 'Learn server-side JavaScript with Node.js',
                        estimated_time: '3 weeks',
                        resources: [
                            { type: 'course', title: 'Node.js Tutorial', url: 'https://nodejs.dev/learn' },
                            { type: 'documentation', title: 'Node.js Docs', url: 'https://nodejs.org/en/docs/' },
                        ],
                        prerequisites: ['JavaScript'],
                        difficulty: 'Intermediate',
                        completed: false,
                    },
                    {
                        step_number: 2,
                        skill: 'MongoDB',
                        description: 'Master NoSQL database with MongoDB',
                        estimated_time: '2 weeks',
                        resources: [
                            { type: 'course', title: 'MongoDB University', url: 'https://university.mongodb.com/' },
                            { type: 'practice', title: 'MongoDB Tutorials', url: 'https://www.mongodb.com/developer/' },
                        ],
                        prerequisites: [],
                        difficulty: 'Beginner',
                        completed: false,
                    },
                    {
                        step_number: 3,
                        skill: 'Docker',
                        description: 'Learn containerization with Docker',
                        estimated_time: '2 weeks',
                        resources: [
                            { type: 'course', title: 'Docker for Beginners', url: 'https://docker-curriculum.com/' },
                            { type: 'practice', title: 'Docker Labs', url: 'https://training.play-with-docker.com/' },
                        ],
                        prerequisites: [],
                        difficulty: 'Intermediate',
                        completed: false,
                    },
                ],
                targetRole: 'Full Stack Developer',
            });
            setLoading(false);
        }, 1000);
    }, []);

    if (loading) {
        return (
            <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 dark:from-slate-900 dark:to-slate-800 flex items-center justify-center">
                <div className="text-center">
                    <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
                    <p className="mt-4 text-slate-600 dark:text-slate-400">Loading your dashboard...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 dark:from-slate-900 dark:to-slate-800">
            {/* Header */}
            <div className="bg-white dark:bg-slate-800 border-b border-slate-200 dark:border-slate-700 px-6 py-6">
                <div className="max-w-7xl mx-auto">
                    <div className="flex items-center justify-between">
                        <div>
                            <h1 className="text-3xl font-bold text-slate-900 dark:text-white mb-2">
                                Career Dashboard
                            </h1>
                            <p className="text-slate-600 dark:text-slate-400">
                                Track your progress and get personalized insights
                            </p>
                        </div>
                        <div className="flex gap-3">
                            <Link
                                href="/resume"
                                className="flex items-center gap-2 px-4 py-2 bg-white dark:bg-slate-700 border border-slate-300 dark:border-slate-600 rounded-lg hover:bg-slate-50 dark:hover:bg-slate-600 transition-colors"
                            >
                                <Upload className="w-4 h-4" />
                                <span>Upload Resume</span>
                            </Link>
                            <Link
                                href="/agent"
                                className="flex items-center gap-2 px-4 py-2 bg-gradient-to-br from-blue-600 to-purple-600 text-white rounded-lg hover:from-blue-700 hover:to-purple-700 transition-all"
                            >
                                <Sparkles className="w-4 h-4" />
                                <span>Ask AI Coach</span>
                            </Link>
                        </div>
                    </div>
                </div>
            </div>

            {/* Main Content */}
            <div className="max-w-7xl mx-auto px-6 py-8 space-y-8">
                {/* Stats Cards */}
                <DashboardStats
                    readinessScore={dashboardData.readinessScore}
                    skillsMatched={dashboardData.skillsMatched}
                    skillsRequired={dashboardData.skillsRequired}
                    predictedSuccessRate={dashboardData.predictedSuccessRate}
                    learningProgress={dashboardData.learningProgress}
                />

                {/* Two Column Layout */}
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                    {/* Left Column - Readiness Gauge */}
                    <div className="lg:col-span-1 space-y-8">
                        <ReadinessGauge score={dashboardData.readinessScore} />
                        <GitHubVerificationBox resumeSkills={dashboardData.matchedSkills} />
                    </div>

                    {/* Right Column - Skill Gap Chart */}
                    <div className="lg:col-span-2">
                        <SkillGapChart
                            matchedSkills={dashboardData.matchedSkills}
                            missingSkills={dashboardData.missingSkills}
                            learningSkills={dashboardData.learningSkills}
                        />
                    </div>
                </div>

                {/* Learning Path */}
                <LearningPathView
                    steps={dashboardData.learningPath}
                    totalTime="7 weeks"
                    targetRole={dashboardData.targetRole}
                />

                {/* Quick Actions */}
                <div className="bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl shadow-lg p-8 text-white">
                    <h2 className="text-2xl font-bold mb-4">Ready to Level Up?</h2>
                    <p className="mb-6 text-blue-100">
                        Get personalized guidance from our AI career coach and accelerate your learning journey.
                    </p>
                    <div className="flex gap-4">
                        <Link
                            href="/agent"
                            className="px-6 py-3 bg-white text-blue-600 rounded-lg font-semibold hover:bg-blue-50 transition-colors"
                        >
                            Talk to AI Coach
                        </Link>
                        <Link
                            href="/resume"
                            className="px-6 py-3 bg-blue-600 bg-opacity-30 backdrop-blur-sm border-2 border-white rounded-lg font-semibold hover:bg-opacity-40 transition-colors"
                        >
                            Analyze Resume
                        </Link>
                        <Link
                            href="/mock-test"
                            className="px-6 py-3 bg-white text-purple-600 rounded-lg font-semibold hover:bg-purple-50 transition-colors"
                        >
                            Take Mock Test
                        </Link>
                    </div>
                </div>
            </div>
        </div>
    );
}
