import Link from 'next/link'
import { ArrowRight, Brain, TrendingUp, Target, Sparkles } from 'lucide-react'

export default function Home() {
    return (
        <main className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
            {/* Navigation */}
            <nav className="container mx-auto px-6 py-6">
                <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                        <Brain className="w-8 h-8 text-purple-400" />
                        <span className="text-2xl font-bold text-white">SkillLens</span>
                    </div>
                    <div className="hidden md:flex items-center space-x-8">
                        <Link href="#features" className="text-gray-300 hover:text-white transition">
                            Features
                        </Link>
                        <Link href="#how-it-works" className="text-gray-300 hover:text-white transition">
                            How It Works
                        </Link>
                        <Link href="/auth" className="text-gray-300 hover:text-white transition">
                            Login
                        </Link>
                        <Link href="/dashboard" className="px-6 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg transition">
                            Get Started
                        </Link>
                    </div>
                </div>
            </nav>

            {/* Hero Section */}
            <section className="container mx-auto px-6 py-20 text-center">
                <div className="max-w-4xl mx-auto animate-fadeIn">
                    <div className="inline-flex items-center space-x-2 px-4 py-2 bg-purple-500/20 rounded-full mb-8 border border-purple-500/30">
                        <Sparkles className="w-4 h-4 text-purple-400" />
                        <span className="text-purple-300 text-sm font-medium">AI-Powered Career Intelligence</span>
                    </div>

                    <h1 className="text-5xl md:text-7xl font-bold text-white mb-6 leading-tight">
                        Predict, Explain, and <br />
                        <span className="bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
                            Optimize Your Career
                        </span>
                    </h1>

                    <p className="text-xl text-gray-300 mb-12 max-w-2xl mx-auto">
                        SkillLens uses semantic NLP, knowledge graphs, and adaptive AI agents to transform
                        your career readiness from guesswork into data-driven intelligence.
                    </p>

                    <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
                        <Link
                            href="/dashboard"
                            className="px-8 py-4 bg-purple-600 hover:bg-purple-700 text-white rounded-lg font-semibold flex items-center space-x-2 transition transform hover:scale-105"
                        >
                            <span>Start Your Assessment</span>
                            <ArrowRight className="w-5 h-5" />
                        </Link>
                        <Link
                            href="#features"
                            className="px-8 py-4 bg-white/10 hover:bg-white/20 text-white rounded-lg font-semibold backdrop-blur-sm border border-white/20 transition"
                        >
                            Learn More
                        </Link>
                    </div>
                </div>
            </section>

            {/* Features Section */}
            <section id="features" className="container mx-auto px-6 py-20">
                <div className="text-center mb-16">
                    <h2 className="text-4xl font-bold text-white mb-4">Powered by Advanced AI</h2>
                    <p className="text-gray-300 text-lg">8 intelligent modules working together for your success</p>
                </div>

                <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
                    {features.map((feature, index) => (
                        <div
                            key={index}
                            className="p-6 bg-white/5 backdrop-blur-sm rounded-xl border border-white/10 hover:border-purple-500/50 transition transform hover:scale-105"
                        >
                            <div className="w-12 h-12 bg-purple-500/20 rounded-lg flex items-center justify-center mb-4">
                                <feature.icon className="w-6 h-6 text-purple-400" />
                            </div>
                            <h3 className="text-xl font-semibold text-white mb-2">{feature.title}</h3>
                            <p className="text-gray-400 text-sm">{feature.description}</p>
                        </div>
                    ))}
                </div>
            </section>

            {/* CTA Section */}
            <section className="container mx-auto px-6 py-20">
                <div className="bg-gradient-to-r from-purple-600 to-pink-600 rounded-2xl p-12 text-center">
                    <h2 className="text-4xl font-bold text-white mb-4">
                        Ready to Transform Your Career?
                    </h2>
                    <p className="text-purple-100 text-lg mb-8 max-w-2xl mx-auto">
                        Join thousands of students and professionals using AI to accelerate their career growth
                    </p>
                    <Link
                        href="/dashboard"
                        className="inline-flex items-center px-8 py-4 bg-white text-purple-600 rounded-lg font-semibold hover:bg-gray-100 transition transform hover:scale-105"
                    >
                        <span>Get Started Free</span>
                        <ArrowRight className="w-5 h-5 ml-2" />
                    </Link>
                </div>
            </section>

            {/* Footer */}
            <footer className="container mx-auto px-6 py-12 border-t border-white/10">
                <div className="text-center text-gray-400">
                    <p>&copy; 2025 SkillLens. AI-Powered Career Intelligence Platform.</p>
                </div>
            </footer>
        </main>
    )
}

const features = [
    {
        icon: Brain,
        title: 'Resume Intelligence',
        description: 'Semantic skill extraction using Sentence-BERT for deep understanding'
    },
    {
        icon: Target,
        title: 'Knowledge Graph',
        description: 'Skill hierarchy and dependency detection with Neo4j'
    },
    {
        icon: TrendingUp,
        title: 'XAI Scoring',
        description: 'Explainable readiness scores with plain-English explanations'
    },
    {
        icon: Sparkles,
        title: 'Prediction Engine',
        description: '30/60/90 day career readiness forecasting'
    },
    {
        icon: Brain,
        title: 'Adaptive Agent',
        description: 'AI agent that evolves your learning path dynamically'
    },
    {
        icon: Target,
        title: 'Skill Verification',
        description: 'AI-generated assessments to validate your skills'
    },
    {
        icon: TrendingUp,
        title: 'Job Intelligence',
        description: 'Real-time job market data and trend analysis'
    },
    {
        icon: Sparkles,
        title: 'Analytics',
        description: 'Institutional dashboards for placement cells'
    },
]
