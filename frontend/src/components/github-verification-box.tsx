'use client';

import { useState } from 'react';
import { Github, CheckCircle, XCircle, Search, ExternalLink, Calendar, Users, Book, ShieldCheck, AlertTriangle } from 'lucide-react';

export default function GitHubVerificationBox() {
    const [username, setUsername] = useState('');
    const [userData, setUserData] = useState<any>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [verified, setVerified] = useState(false);

    const checkGitHub = async () => {
        if (!username) return;

        setLoading(true);
        setError(null);
        setUserData(null);
        setVerified(false);

        try {
            const response = await fetch(`https://api.github.com/users/${username}`);

            if (!response.ok) {
                if (response.status === 404) {
                    throw new Error('User not found');
                }
                throw new Error('Failed to fetch GitHub data');
            }

            const data = await response.json();
            setUserData(data);

            // Verification logic: User exists and has at least one public repo
            if (data.public_repos > 0) {
                setVerified(true);
            } else {
                setError('User has no public repositories to verify skills against.');
            }

        } catch (err: any) {
            setError(err.message || 'An error occurred');
        } finally {
            setLoading(false);
        }
    };

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter') {
            checkGitHub();
        }
    };

    return (
        <div className="bg-white dark:bg-slate-800 rounded-xl shadow-lg border border-slate-200 dark:border-slate-700 p-6 transition-all hover:shadow-xl">
            <div className="flex items-center gap-3 mb-6">
                <div className="p-2.5 bg-gradient-to-br from-slate-800 to-slate-900 rounded-lg shadow-sm">
                    <Github className="w-5 h-5 text-white" />
                </div>
                <div>
                    <h3 className="text-lg font-bold text-slate-900 dark:text-white leading-tight">
                        GitHub Verification
                    </h3>
                    <p className="text-xs text-slate-500 dark:text-slate-400 font-medium">
                        Link your portfolio
                    </p>
                </div>
            </div>

            <div className="space-y-4">
                <div className="relative group">
                    <input
                        type="text"
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                        onKeyDown={handleKeyDown}
                        placeholder="Enter GitHub username"
                        className="w-full px-4 py-2.5 pl-10 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500 transition-all text-slate-900 dark:text-white placeholder-slate-400 text-sm"
                    />
                    <Search className="absolute left-3 top-3 w-4 h-4 text-slate-400 group-focus-within:text-blue-500 transition-colors" />
                </div>

                <button
                    onClick={checkGitHub}
                    disabled={loading || !username}
                    className="w-full px-4 py-2.5 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white rounded-lg font-semibold text-sm shadow-md hover:shadow-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 transform active:scale-[0.98]"
                >
                    {loading ? (
                        <>
                            <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                            <span>Verifying...</span>
                        </>
                    ) : (
                        <>
                            <ShieldCheck className="w-4 h-4" />
                            <span>Verify Profile</span>
                        </>
                    )}
                </button>

                {error && (
                    <div className="p-3 bg-red-50 dark:bg-red-900/10 border border-red-200 dark:border-red-900/30 rounded-lg flex gap-3 items-start animate-fadeIn">
                        <AlertTriangle className="w-5 h-5 text-red-500 shrink-0 mt-0.5" />
                        <p className="text-xs text-red-600 dark:text-red-400 font-medium leading-relaxed">{error}</p>
                    </div>
                )}

                {userData && (
                    <div className="mt-4 pt-4 border-t border-slate-100 dark:border-slate-700 animate-fadeIn">
                        <div className="flex items-start gap-3 mb-4">
                            <img
                                src={userData.avatar_url}
                                alt={userData.login}
                                className="w-12 h-12 rounded-full border-2 border-slate-100 dark:border-slate-700 shadow-sm"
                            />
                            <div className="flex-1 min-w-0">
                                <div className="flex items-center gap-2 flex-wrap">
                                    <h4 className="font-bold text-slate-900 dark:text-white truncate text-sm">
                                        {userData.name || userData.login}
                                    </h4>
                                    {verified && (
                                        <span className="px-1.5 py-0.5 bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400 text-[10px] font-bold rounded-md flex items-center gap-0.5 border border-green-200 dark:border-green-800">
                                            <CheckCircle className="w-3 h-3" />
                                            VERIFIED
                                        </span>
                                    )}
                                </div>
                                <a
                                    href={userData.html_url}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="text-xs text-blue-600 dark:text-blue-400 hover:underline flex items-center gap-1 mt-0.5"
                                >
                                    @{userData.login}
                                    <ExternalLink className="w-3 h-3" />
                                </a>
                            </div>
                        </div>

                        {userData.bio && (
                            <div className="bg-slate-50 dark:bg-slate-900/50 p-3 rounded-lg mb-4 border border-slate-100 dark:border-slate-800">
                                <p className="text-xs text-slate-600 dark:text-slate-300 italic line-clamp-3">
                                    "{userData.bio}"
                                </p>
                            </div>
                        )}

                        <div className="grid grid-cols-3 gap-2">
                            <div className="p-2 bg-slate-50 dark:bg-slate-900/50 rounded-lg text-center border border-slate-100 dark:border-slate-800">
                                <Book className="w-4 h-4 mx-auto mb-1 text-blue-500" />
                                <span className="font-bold text-slate-900 dark:text-white block text-sm">{userData.public_repos}</span>
                                <span className="text-[10px] text-slate-500 uppercase tracking-wide font-medium">Repos</span>
                            </div>
                            <div className="p-2 bg-slate-50 dark:bg-slate-900/50 rounded-lg text-center border border-slate-100 dark:border-slate-800">
                                <Users className="w-4 h-4 mx-auto mb-1 text-purple-500" />
                                <span className="font-bold text-slate-900 dark:text-white block text-sm">{userData.followers}</span>
                                <span className="text-[10px] text-slate-500 uppercase tracking-wide font-medium">Followers</span>
                            </div>
                            <div className="p-2 bg-slate-50 dark:bg-slate-900/50 rounded-lg text-center border border-slate-100 dark:border-slate-800">
                                <Calendar className="w-4 h-4 mx-auto mb-1 text-orange-500" />
                                <span className="font-bold text-slate-900 dark:text-white block text-sm">
                                    {new Date(userData.created_at).getFullYear()}
                                </span>
                                <span className="text-[10px] text-slate-500 uppercase tracking-wide font-medium">Joined</span>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}
