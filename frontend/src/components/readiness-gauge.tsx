'use client';

interface ReadinessGaugeProps {
    score: number; // 0-100
    label?: string;
}

export default function ReadinessGauge({ score = 0, label = 'Career Readiness' }: ReadinessGaugeProps) {
    // Clamp score between 0 and 100
    const clampedScore = Math.max(0, Math.min(100, score));

    // Determine color based on score
    const getColor = (score: number) => {
        if (score >= 80) return { from: '#10b981', to: '#059669', text: 'text-green-600' }; // green
        if (score >= 60) return { from: '#3b82f6', to: '#2563eb', text: 'text-blue-600' }; // blue
        if (score >= 40) return { from: '#f59e0b', to: '#d97706', text: 'text-orange-600' }; // orange
        return { from: '#ef4444', to: '#dc2626', text: 'text-red-600' }; // red
    };

    const color = getColor(clampedScore);

    // Calculate stroke dasharray for circular progress
    const radius = 70;
    const circumference = 2 * Math.PI * radius;
    const strokeDashoffset = circumference - (clampedScore / 100) * circumference;

    return (
        <div className="bg-white dark:bg-slate-800 rounded-xl shadow-lg border border-slate-200 dark:border-slate-700 p-6">
            <h2 className="text-xl font-bold text-slate-900 dark:text-white mb-6 text-center">
                {label}
            </h2>

            <div className="relative flex items-center justify-center">
                <svg className="transform -rotate-90" width="200" height="200">
                    {/* Background circle */}
                    <circle
                        cx="100"
                        cy="100"
                        r={radius}
                        stroke="#e2e8f0"
                        strokeWidth="12"
                        fill="none"
                    />

                    {/* Progress circle */}
                    <circle
                        cx="100"
                        cy="100"
                        r={radius}
                        stroke={`url(#gradient-${clampedScore})`}
                        strokeWidth="12"
                        fill="none"
                        strokeLinecap="round"
                        strokeDasharray={circumference}
                        strokeDashoffset={strokeDashoffset}
                        className="transition-all duration-1000 ease-out"
                    />

                    {/* Gradient definition */}
                    <defs>
                        <linearGradient id={`gradient-${clampedScore}`} x1="0%" y1="0%" x2="100%" y2="100%">
                            <stop offset="0%" stopColor={color.from} />
                            <stop offset="100%" stopColor={color.to} />
                        </linearGradient>
                    </defs>
                </svg>

                {/* Score text */}
                <div className="absolute inset-0 flex flex-col items-center justify-center">
                    <span className={`text-5xl font-bold ${color.text}`}>
                        {clampedScore}
                    </span>
                    <span className="text-sm text-slate-600 dark:text-slate-400 mt-1">
                        out of 100
                    </span>
                </div>
            </div>

            {/* Status message */}
            <div className="mt-6 text-center">
                <p className="text-sm font-medium text-slate-700 dark:text-slate-300">
                    {clampedScore >= 80 && '🎉 Excellent! You\'re ready to apply!'}
                    {clampedScore >= 60 && clampedScore < 80 && '👍 Good progress! Minor improvements needed.'}
                    {clampedScore >= 40 && clampedScore < 60 && '📚 Keep learning! You\'re on the right track.'}
                    {clampedScore < 40 && '💪 Let\'s build your skills together!'}
                </p>
            </div>
        </div>
    );
}
