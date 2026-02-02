'use client'

import { useState } from 'react'
import Link from 'next/link'
import { Brain, Upload, ArrowLeft, FileText, CheckCircle, AlertCircle, Loader2 } from 'lucide-react'

const API_URL = 'http://127.0.0.1:8000'

export default function ResumeUpload() {
    const [file, setFile] = useState<File | null>(null)
    const [uploading, setUploading] = useState(false)
    const [result, setResult] = useState<any>(null)
    const [error, setError] = useState<string | null>(null)

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            const selectedFile = e.target.files[0]
            const ext = selectedFile.name.split('.').pop()?.toLowerCase()

            if (ext !== 'pdf' && ext !== 'docx' && ext !== 'doc') {
                setError('Only PDF and DOCX files are supported')
                return
            }

            setFile(selectedFile)
            setError(null)
            setResult(null)
        }
    }

    const handleUpload = async () => {
        if (!file) return

        setUploading(true)
        setError(null)

        try {
            // Get authentication token and user info
            const token = localStorage.getItem('token')
            const userStr = localStorage.getItem('user')

            if (!token || !userStr) {
                throw new Error('Please login first')
            }

            const user = JSON.parse(userStr)
            const userId = user.user_id

            const formData = new FormData()
            formData.append('file', file)

            const response = await fetch(`${API_URL}/api/resume/upload?user_id=${userId}`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`
                },
                body: formData
            })

            if (!response.ok) {
                const errorData = await response.json()
                throw new Error(errorData.detail || 'Upload failed')
            }

            const data = await response.json()
            setResult(data)
        } catch (err: any) {
            setError(err.message || 'Failed to upload and parse resume. Make sure the backend is running.')
        } finally {
            setUploading(false)
        }
    }

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
            <nav className="container mx-auto px-6 py-6">
                <div className="flex items-center justify-between">
                    <Link href="/" className="flex items-center space-x-2">
                        <Brain className="w-8 h-8 text-purple-400" />
                        <span className="text-2xl font-bold text-white">SkillLens</span>
                    </Link>
                    <Link href="/dashboard" className="flex items-center space-x-2 text-gray-300 hover:text-white transition">
                        <ArrowLeft className="w-4 h-4" />
                        <span>Back to Dashboard</span>
                    </Link>
                </div>
            </nav>

            <div className="container mx-auto px-6 py-12">
                <div className="max-w-4xl mx-auto">
                    <div className="mb-12 text-center">
                        <h1 className="text-4xl font-bold text-white mb-4">Upload Your Resume</h1>
                        <p className="text-gray-300 text-lg">AI-powered resume analysis with Sentence-BERT and NER</p>
                    </div>

                    {/* Upload Section */}
                    <div className="bg-white/5 backdrop-blur-sm rounded-xl border border-white/10 p-8 mb-6">
                        <div className="mb-8">
                            <div className="w-24 h-24 bg-purple-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
                                <Upload className="w-12 h-12 text-purple-400" />
                            </div>
                            <h2 className="text-2xl font-bold text-white text-center mb-2">Upload Resume</h2>
                            <p className="text-gray-400 text-center">
                                Supported formats: PDF, DOCX (Max 10MB)
                            </p>
                        </div>

                        <div className="max-w-md mx-auto">
                            <div className="border-2 border-dashed border-purple-500/50 rounded-lg p-8 mb-4 hover:border-purple-500 transition">
                                <input
                                    type="file"
                                    accept=".pdf,.docx,.doc"
                                    onChange={handleFileChange}
                                    className="hidden"
                                    id="resume-upload"
                                />
                                <label htmlFor="resume-upload" className="cursor-pointer block">
                                    {file ? (
                                        <div className="text-white text-center">
                                            <FileText className="w-12 h-12 mx-auto mb-2 text-green-400" />
                                            <p className="font-semibold">{file.name}</p>
                                            <p className="text-sm text-gray-400 mt-1">
                                                {(file.size / 1024 / 1024).toFixed(2)} MB
                                            </p>
                                        </div>
                                    ) : (
                                        <div className="text-gray-400 text-center">
                                            <Upload className="w-12 h-12 mx-auto mb-2" />
                                            <p>Click to browse or drag and drop</p>
                                            <p className="text-sm mt-1">PDF or DOCX files only</p>
                                        </div>
                                    )}
                                </label>
                            </div>

                            {error && (
                                <div className="mb-4 p-4 bg-red-500/20 border border-red-500/50 rounded-lg flex items-center space-x-2">
                                    <AlertCircle className="w-5 h-5 text-red-400" />
                                    <p className="text-red-300 text-sm">{error}</p>
                                </div>
                            )}

                            <button
                                onClick={handleUpload}
                                disabled={!file || uploading}
                                className="w-full px-6 py-3 bg-purple-600 hover:bg-purple-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white rounded-lg font-semibold transition flex items-center justify-center"
                            >
                                {uploading ? (
                                    <>
                                        <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                                        Analyzing with AI...
                                    </>
                                ) : (
                                    <>
                                        <Upload className="w-5 h-5 mr-2" />
                                        Upload and Analyze
                                    </>
                                )}
                            </button>
                        </div>
                    </div>

                    {/* Results Section */}
                    {result && (
                        <div className="space-y-6 animate-fadeIn">
                            {/* Quality Score */}
                            <div className="bg-white/5 backdrop-blur-sm rounded-xl border border-white/10 p-8">
                                <div className="flex items-center justify-between mb-6">
                                    <h3 className="text-2xl font-bold text-white">Resume Quality Score</h3>
                                    <CheckCircle className="w-8 h-8 text-green-400" />
                                </div>
                                <div className="text-center mb-6">
                                    <div className="text-6xl font-bold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
                                        {result.parsed_data?.quality_score?.toFixed(1) ?? 'N/A'}/100
                                    </div>
                                    <p className="text-gray-300 mt-2">{result.insights?.resume_quality ?? 'Resume uploaded successfully'}</p>
                                </div>
                                <div className="grid grid-cols-3 gap-4 text-center">
                                    <div className="bg-white/5 rounded-lg p-4">
                                        <div className="text-2xl font-bold text-purple-400">{result.insights?.total_skills ?? result.parsed_data?.skills?.length ?? 0}</div>
                                        <div className="text-sm text-gray-400">Skills Found</div>
                                    </div>
                                    <div className="bg-white/5 rounded-lg p-4">
                                        <div className="text-2xl font-bold text-blue-400">{result.insights?.experience_count ?? result.parsed_data?.experience?.length ?? 0}</div>
                                        <div className="text-sm text-gray-400">Experience</div>
                                    </div>
                                    <div className="bg-white/5 rounded-lg p-4">
                                        <div className="text-2xl font-bold text-green-400">{result.insights?.project_count ?? result.parsed_data?.projects?.length ?? 0}</div>
                                        <div className="text-sm text-gray-400">Projects</div>
                                    </div>
                                </div>
                            </div>

                            {/* Extracted Skills */}
                            <div className="bg-white/5 backdrop-blur-sm rounded-xl border border-white/10 p-8">
                                <h3 className="text-2xl font-bold text-white mb-4">Extracted Skills</h3>
                                <div className="flex flex-wrap gap-2">
                                    {result.parsed_data?.skills && result.parsed_data.skills.length > 0 ? (
                                        result.parsed_data.skills.map((skill: string) => (
                                            <span key={skill} className="px-3 py-1 bg-purple-500/20 border border-purple-500/50 rounded-full text-purple-300 text-sm">
                                                {skill}
                                            </span>
                                        ))
                                    ) : (
                                        <p className="text-gray-400">No skills extracted yet</p>
                                    )}
                                </div>
                            </div>

                            {/* AI Insights */}
                            <div className="bg-white/5 backdrop-blur-sm rounded-xl border border-white/10 p-8">
                                <h3 className="text-2xl font-bold text-white mb-4">AI-Powered Insights</h3>
                                <div className="space-y-4 text-gray-300">
                                    <div className="flex items-start space-x-2">
                                        <CheckCircle className="w-5 h-5 text-green-400 mt-1" />
                                        <div>
                                            <p className="font-semibold text-white">Semantic Analysis Complete</p>
                                            <p className="text-sm">
                                                {result.parsed_data?.embedding_dimension
                                                    ? `Generated ${result.parsed_data.embedding_dimension}-dimensional semantic embeddings using Sentence-BERT`
                                                    : 'Resume processed with AI-powered semantic analysis'}
                                            </p>
                                        </div>
                                    </div>
                                    <div className="flex items-start space-x-2">
                                        <CheckCircle className="w-5 h-5 text-green-400 mt-1" />
                                        <div>
                                            <p className="font-semibold text-white">Entity Extraction</p>
                                            <p className="text-sm">
                                                {result.parsed_data?.entities
                                                    ? `Identified ${Object.values(result.parsed_data.entities).flat().length} entities using BERT-NER`
                                                    : 'Resume parsed and ready for analysis'}
                                            </p>
                                        </div>
                                    </div>
                                    <div className="flex items-start space-x-2">
                                        <CheckCircle className="w-5 h-5 text-green-400 mt-1" />
                                        <div>
                                            <p className="font-semibold text-white">Ready for Analysis</p>
                                            <p className="text-sm">Your resume has been processed and is ready for skill gap analysis and career readiness scoring</p>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            {/* Next Steps */}
                            <div className="bg-gradient-to-r from-purple-600 to-pink-600 rounded-xl p-8 text-center">
                                <h3 className="text-2xl font-bold text-white mb-4">What's Next?</h3>
                                <p className="text-purple-100 mb-6">
                                    Now that your resume is analyzed, get personalized career insights
                                </p>
                                <Link href="/dashboard" className="inline-block px-8 py-3 bg-white text-purple-600 rounded-lg font-semibold hover:bg-gray-100 transition">
                                    View Career Dashboard →
                                </Link>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    )
}
