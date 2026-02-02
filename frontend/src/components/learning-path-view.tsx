'use client';

import { CheckCircle2, Circle, Clock, ExternalLink } from 'lucide-react';

interface LearningStep {
    step_number: number;
    skill: string;
    description: string;
    estimated_time: string;
    resources: Array<{
        type: string;
        title: string;
        url: string;
    }>;
    prerequisites: string[];
    difficulty: string;
    completed?: boolean;
}

interface LearningPathViewProps {
    steps?: LearningStep[];
    totalTime?: string;
    targetRole?: string;
}

export default function LearningPathView({
    steps = [],
    totalTime = '0 weeks',
    targetRole = 'Your Target Role',
}: LearningPathViewProps) {
    const difficultyColors = {
        Beginner: 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400',
        Intermediate: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400',
        Advanced: 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400',
    };

    const resourceIcons = {
        course: '📚',
        documentation: '📖',
        practice: '💻',
        search: '🔍',
    };

    return (
        <div className="bg-white dark:bg-slate-800 rounded-xl shadow-lg border border-slate-200 dark:border-slate-700 p-6">
            {/* Header */}
            <div className="mb-6">
                <h2 className="text-xl font-bold text-slate-900 dark:text-white mb-2">
                    Learning Path: {targetRole}
                </h2>
                <div className="flex items-center gap-4 text-sm text-slate-600 dark:text-slate-400">
                    <div className="flex items-center gap-1">
                        <Clock className="w-4 h-4" />
                        <span>Total Time: {totalTime}</span>
                    </div>
                    <div className="flex items-center gap-1">
                        <Circle className="w-4 h-4" />
                        <span>{steps.length} Steps</span>
                    </div>
                </div>
            </div>

            {/* Steps */}
            {steps.length > 0 ? (
                <div className="space-y-6">
                    {steps.map((step, index) => (
                        <div key={step.step_number} className="relative">
                            {/* Connector Line */}
                            {index < steps.length - 1 && (
                                <div className="absolute left-5 top-12 bottom-0 w-0.5 bg-slate-200 dark:bg-slate-700" />
                            )}

                            {/* Step Card */}
                            <div className="relative flex gap-4">
                                {/* Step Number */}
                                <div className="flex-shrink-0">
                                    {step.completed ? (
                                        <div className="w-10 h-10 bg-green-500 rounded-full flex items-center justify-center">
                                            <CheckCircle2 className="w-6 h-6 text-white" />
                                        </div>
                                    ) : (
                                        <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white font-bold">
                                            {step.step_number}
                                        </div>
                                    )}
                                </div>

                                {/* Step Content */}
                                <div className="flex-1 bg-slate-50 dark:bg-slate-900/50 rounded-lg p-4 border border-slate-200 dark:border-slate-700">
                                    <div className="flex items-start justify-between mb-2">
                                        <h3 className="text-lg font-semibold text-slate-900 dark:text-white">
                                            {step.skill}
                                        </h3>
                                        <span className={`px-2 py-1 rounded text-xs font-medium ${difficultyColors[step.difficulty as keyof typeof difficultyColors] || difficultyColors.Beginner}`}>
                                            {step.difficulty}
                                        </span>
                                    </div>

                                    <p className="text-sm text-slate-600 dark:text-slate-400 mb-3">
                                        {step.description}
                                    </p>

                                    <div className="flex items-center gap-4 text-xs text-slate-500 dark:text-slate-400 mb-3">
                                        <span>⏱️ {step.estimated_time}</span>
                                        {step.prerequisites.length > 0 && (
                                            <span>📋 Prerequisites: {step.prerequisites.join(', ')}</span>
                                        )}
                                    </div>

                                    {/* Resources */}
                                    {step.resources.length > 0 && (
                                        <div className="space-y-2">
                                            <p className="text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wide">
                                                Resources
                                            </p>
                                            <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                                                {step.resources.map((resource, idx) => (
                                                    <a
                                                        key={idx}
                                                        href={resource.url}
                                                        target="_blank"
                                                        rel="noopener noreferrer"
                                                        className="flex items-center gap-2 px-3 py-2 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg hover:bg-blue-50 dark:hover:bg-slate-700 transition-colors group"
                                                    >
                                                        <span>{resourceIcons[resource.type as keyof typeof resourceIcons] || '📄'}</span>
                                                        <span className="text-sm text-slate-700 dark:text-slate-300 flex-1 truncate">
                                                            {resource.title}
                                                        </span>
                                                        <ExternalLink className="w-3 h-3 text-slate-400 group-hover:text-blue-600" />
                                                    </a>
                                                ))}
                                            </div>
                                        </div>
                                    )}
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            ) : (
                <div className="text-center py-12 text-slate-500 dark:text-slate-400">
                    <Circle className="w-16 h-16 mx-auto mb-4 opacity-50" />
                    <p className="text-lg font-medium mb-2">No Learning Path Yet</p>
                    <p className="text-sm">Generate a personalized learning path using the AI agent!</p>
                </div>
            )}
        </div>
    );
}
