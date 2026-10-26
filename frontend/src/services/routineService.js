/**
 * Routine Service
 * Handles all API calls for the Routine Build module
 */

import { getStoredToken } from './authService';
import { API_BASE_URL } from '../config/api';

const authHeaders = () => {
    const token = getStoredToken();
    return {
        'Content-Type': 'application/json',
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
    };
};

/**
 * Generate a learning routine from uploaded analysis file
 */
export const generateRoutineFromFile = async (file, hoursPerWeek = 10) => {
    try {
        const token = getStoredToken();
        if (!token) throw new Error('Authentication required');

        // Get the target domain the user selected in the Analyze module
        const analyzeTargetDomain = localStorage.getItem('analyzeTargetDomain') || '';
        // Fallback to user's profile domain if analyze domain not found
        const storedUser = localStorage.getItem('user');
        const profileDomain = storedUser ? JSON.parse(storedUser)?.domain || '' : '';
        const userDomain = analyzeTargetDomain || profileDomain;

        const formData = new FormData();
        formData.append('file', file);
        formData.append('hoursPerWeek', String(hoursPerWeek));
        if (userDomain) formData.append('userDomain', userDomain);

        const response = await fetch(`${API_BASE_URL}/api/routine/generate`, {
            method: 'POST',
            headers: {
                ...(token ? { Authorization: `Bearer ${token}` } : {}),
            },
            body: formData,
        });

        const result = await response.json();
        if (!response.ok) {
            if (response.status === 401) throw new Error('Session expired. Please login again.');
            throw new Error(result.message || 'Routine generation failed');
        }
        return result;
    } catch (error) {
        console.error('generateRoutineFromFile error:', error);
        return { success: false, message: error.message || 'Network error' };
    }
};

/**
 * Update skill progress with new endpoint
 */
export const updateRoutineProgress = async (week, skill, completionPercentage, date, routineData) => {
    try {
        const token = getStoredToken();
        if (!token) throw new Error('Authentication required');

        const response = await fetch(`${API_BASE_URL}/api/routine/progress`, {
            method: 'POST',
            headers: authHeaders(),
            body: JSON.stringify({
                week,
                skill,
                completionPercentage,
                date,
                routineData
            }),
        });

        const result = await response.json();
        if (!response.ok) {
            if (response.status === 401) throw new Error('Session expired. Please login again.');
            throw new Error(result.message || 'Progress update failed');
        }
        return result;
    } catch (error) {
        console.error('updateRoutineProgress error:', error);
        return { success: false, message: error.message || 'Network error' };
    }
};

/**
 * Chat with AI Mentor about routine
 */
export const routineChat = async (userQuestion, routineData = null, progressData = null) => {
    try {
        const token = getStoredToken();
        if (!token) throw new Error('Authentication required');

        const response = await fetch(`${API_BASE_URL}/api/routine/chat`, {
            method: 'POST',
            headers: authHeaders(),
            body: JSON.stringify({
                userQuestion,
                routineData,
                progressData
            }),
        });

        const result = await response.json();
        if (!response.ok) {
            if (response.status === 401) throw new Error('Session expired. Please login again.');
            throw new Error(result.message || 'Chat failed');
        }
        return result;
    } catch (error) {
        console.error('routineChat error:', error);
        return { 
            success: false, 
            response: 'Sorry, I could not process your question. Please try again.',
            message: error.message || 'Network error' 
        };
    }
};
