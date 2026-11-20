/**
 * API client for SkillLens backend
 */

import axios from 'axios'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export const api = axios.create({
    baseURL: API_URL,
    headers: {
        'Content-Type': 'application/json',
    },
})

// Resume API
export const resumeAPI = {
    upload: async (file: File, userId: string = 'demo_user') => {
        const formData = new FormData()
        formData.append('file', file)
        formData.append('user_id', userId)

        const response = await api.post('/api/resume/upload', formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        })
        return response.data
    },

    getByUserId: async (userId: string) => {
        const response = await api.get(`/api/resume/${userId}`)
        return response.data
    },

    list: async (skip: number = 0, limit: number = 10) => {
        const response = await api.get('/api/resume/', {
            params: { skip, limit },
        })
        return response.data
    },
}

// Skills API
export const skillsAPI = {
    initialize: async () => {
        const response = await api.post('/api/skills/initialize')
        return response.data
    },

    getHierarchy: async () => {
        const response = await api.get('/api/skills/hierarchy')
        return response.data
    },

    analyzeGap: async (userSkills: string[], targetRole: string) => {
        const response = await api.post('/api/skills/gap-analysis', {
            user_skills: userSkills,
            target_role: targetRole,
        })
        return response.data
    },

    getDependencies: async (skill: string) => {
        const response = await api.get(`/api/skills/dependencies/${skill}`)
        return response.data
    },

    getLearningPath: async (userSkills: string[], targetRole: string) => {
        const response = await api.post('/api/skills/learning-path', {
            user_skills: userSkills,
            target_role: targetRole,
        })
        return response.data
    },
}

// Scoring API
export const scoringAPI = {
    calculateReadiness: async (userId: string, targetRole: string) => {
        const response = await api.post('/api/scoring/readiness', {
            user_id: userId,
            target_role: targetRole,
            include_explanation: true,
        })
        return response.data
    },

    getHistory: async (userId: string, targetRole?: string, limit: number = 10) => {
        const response = await api.get(`/api/scoring/history/${userId}`, {
            params: { target_role: targetRole, limit },
        })
        return response.data
    },

    getExplanation: async (userId: string) => {
        const response = await api.get(`/api/scoring/explanation/${userId}`)
        return response.data
    },
}

// Health check
export const healthCheck = async () => {
    const response = await api.get('/health')
    return response.data
}

export default api
