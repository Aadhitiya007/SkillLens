'use client';

import { TrendingUp, Target, Award, BookOpen } from 'lucide-react';

interface StatsCardProps {
    title: string;
    value: string | number;
    subtitle?: string;
    icon: React.ReactNode;
    trend?: {
        value: number;
        isPositive: boolean;
    };
    color: 'blue' | 'green' | 'purple' | 'orange';
}

const colorClasses = {
    blue: 'from-blue-500 to-blue-600',
    green: 'from-green-500 to-green-600',
    purple: 'from-purple-500 to-purple-600',
    orange: 'from-orange-500 to-orange-600',
};

function StatsCard({ title, value, subtitle, icon, trend, color }: StatsCardProps) {
    return (
        <div className="bg-white dark:bg-slate-800 rounded-xl shadow-lg border border-slate-200 dark:border-slate-700 p-6 hover:shadow-xl transition-shadow">
            <div className="flex items-start justify-between">
                <div className="flex-1">
                    <p className="text-sm font-medium text-slate-600 dark:text-slate-400 mb-1">
                        {title}
                    </p>
                    <p className="text-3xl font-bold text-slate-900 dark:text-white mb-1">
                        {value}
                    </p>
                    {subtitle && (
                        <p className="text-xs text-slate-500 dark:text-slate-400">
                            {subtitle}
                        </p>
                    )}
                    {trend && (
                        <div className={`flex items-center gap-1 mt-2 text-sm ${trend.isPositive ? 'text-green-600' : 'text-red-600'}`}>
                            <TrendingUp className={`w-4 h-4 ${!trend.isPositive && 'rotate-180'}`} />
                            <span>{Math.abs(trend.value)}% from last month</span>
                        </div>
                    )}
                </div>
                <div className={`p-3 bg-gradient-to-br ${colorClasses[color]} rounded-lg`}>
                    <div className="text-white">
                        {icon}
                    </div>
                </div>
            </div>
        </div>
    );
}

interface DashboardStatsProps {
    readinessScore?: number;
    skillsMatched?: number;
    skillsRequired?: number;
    predictedSuccessRate?: number;
    learningProgress?: number;
}

export default function DashboardStats({
    readinessScore = 0,
    skillsMatched = 0,
    skillsRequired = 0,
    predictedSuccessRate = 0,
    learningProgress = 0,
}: DashboardStatsProps) {
    return (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <StatsCard
                title="Career Readiness"
                value={`${readinessScore}%`}
                subtitle="Overall readiness score"
                icon={<Target className="w-6 h-6" />}
                color="blue"
                trend={{
                    value: 12,
                    isPositive: true,
                }}
            />

            <StatsCard
                title="Skills Match"
                value={`${skillsMatched}/${skillsRequired}`}
                subtitle="Matched vs Required"
                icon={<Award className="w-6 h-6" />}
                color="green"
            />

            <StatsCard
                title="Success Rate"
                value={`${predictedSuccessRate}%`}
                subtitle="Predicted shortlisting"
                icon={<TrendingUp className="w-6 h-6" />}
                color="purple"
                trend={{
                    value: 8,
                    isPositive: true,
                }}
            />

            <StatsCard
                title="Learning Progress"
                value={`${learningProgress}%`}
                subtitle="Path completion"
                icon={<BookOpen className="w-6 h-6" />}
                color="orange"
            />
        </div>
    );
}
