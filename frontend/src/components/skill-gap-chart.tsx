'use client';

import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell } from 'recharts';

interface SkillGapData {
    skill: string;
    status: 'matched' | 'missing' | 'learning';
    category: string;
}

interface SkillGapChartProps {
    matchedSkills?: string[];
    missingSkills?: string[];
    learningSkills?: string[];
}

export default function SkillGapChart({
    matchedSkills = [],
    missingSkills = [],
    learningSkills = [],
}: SkillGapChartProps) {
    // Prepare data for chart
    const data = [
        {
            name: 'Matched',
            count: matchedSkills.length,
            color: '#10b981', // green
        },
        {
            name: 'Learning',
            count: learningSkills.length,
            color: '#f59e0b', // orange
        },
        {
            name: 'Missing',
            count: missingSkills.length,
            color: '#ef4444', // red
        },
    ];

    // Detailed skill list
    const allSkills: SkillGapData[] = [
        ...matchedSkills.map(skill => ({ skill, status: 'matched' as const, category: 'Technical' })),
        ...learningSkills.map(skill => ({ skill, status: 'learning' as const, category: 'Technical' })),
        ...missingSkills.map(skill => ({ skill, status: 'missing' as const, category: 'Technical' })),
    ];

    const statusColors = {
        matched: 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400',
        learning: 'bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-400',
        missing: 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400',
    };

    const statusLabels = {
        matched: 'Matched ✓',
        learning: 'Learning...',
        missing: 'Missing',
    };

    return (
        <div className="bg-white dark:bg-slate-800 rounded-xl shadow-lg border border-slate-200 dark:border-slate-700 p-6">
            <h2 className="text-xl font-bold text-slate-900 dark:text-white mb-6">
                Skill Gap Analysis
            </h2>

            {/* Chart */}
            <div className="mb-8">
                <ResponsiveContainer width="100%" height={250}>
                    <BarChart data={data}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                        <XAxis dataKey="name" stroke="#64748b" />
                        <YAxis stroke="#64748b" />
                        <Tooltip
                            contentStyle={{
                                backgroundColor: '#1e293b',
                                border: 'none',
                                borderRadius: '8px',
                                color: '#fff',
                            }}
                        />
                        <Bar dataKey="count" radius={[8, 8, 0, 0]}>
                            {data.map((entry, index) => (
                                <Cell key={`cell-${index}`} fill={entry.color} />
                            ))}
                        </Bar>
                    </BarChart>
                </ResponsiveContainer>
            </div>

            {/* Skill List */}
            <div className="space-y-4">
                <h3 className="text-sm font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wide">
                    Detailed Skills
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                    {allSkills.map((item, index) => (
                        <div
                            key={index}
                            className={`px-3 py-2 rounded-lg text-sm font-medium ${statusColors[item.status]}`}
                        >
                            <div className="flex items-center justify-between">
                                <span>{item.skill}</span>
                                <span className="text-xs opacity-75">{statusLabels[item.status]}</span>
                            </div>
                        </div>
                    ))}
                </div>

                {allSkills.length === 0 && (
                    <div className="text-center py-8 text-slate-500 dark:text-slate-400">
                        <p>No skill data available. Upload your resume to get started!</p>
                    </div>
                )}
            </div>

            {/* Summary */}
            <div className="mt-6 pt-6 border-t border-slate-200 dark:border-slate-700">
                <div className="grid grid-cols-3 gap-4 text-center">
                    <div>
                        <p className="text-2xl font-bold text-green-600 dark:text-green-400">
                            {matchedSkills.length}
                        </p>
                        <p className="text-xs text-slate-600 dark:text-slate-400 mt-1">Matched</p>
                    </div>
                    <div>
                        <p className="text-2xl font-bold text-orange-600 dark:text-orange-400">
                            {learningSkills.length}
                        </p>
                        <p className="text-xs text-slate-600 dark:text-slate-400 mt-1">Learning</p>
                    </div>
                    <div>
                        <p className="text-2xl font-bold text-red-600 dark:text-red-400">
                            {missingSkills.length}
                        </p>
                        <p className="text-xs text-slate-600 dark:text-slate-400 mt-1">Missing</p>
                    </div>
                </div>
            </div>
        </div>
    );
}
