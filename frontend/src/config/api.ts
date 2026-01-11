// ============================================
// API Configuration
// ============================================

// Base URL is handled by Vite proxy in development
// In production, this would be the actual API URL
export const API_BASE_URL = '';

// API Endpoints
export const API_ENDPOINTS = {
    GENERATE_POST: '/generate-post',
    APPROVE_POST: '/approve-post',
    LINKEDIN_STATUS: '/linkedin/status',
    LINKEDIN_CONNECT: '/linkedin/connect',
    LINKEDIN_DISCONNECT: '/linkedin/disconnect',
} as const;

// Helper function for API requests
export async function apiRequest<T>(
    endpoint: string,
    options: RequestInit = {}
): Promise<T> {
    const defaultHeaders: HeadersInit = {
        'Content-Type': 'application/json',
    };

    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        ...options,
        headers: {
            ...defaultHeaders,
            ...options.headers,
        },
    });

    if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }

    return response.json();
}
