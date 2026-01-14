// ============================================
// LinkedIn Service - OAuth and connection APIs
// ============================================

import { apiRequest, API_ENDPOINTS } from '@/config/api';
import type { LinkedInStatus, LinkedInConnectResponse, LinkedInDisconnectResponse } from '@/types';

/**
 * Check LinkedIn connection status
 */
export async function getLinkedInStatus(userId?: string): Promise<LinkedInStatus> {
    const query = userId ? `?user_id=${userId}` : '';
    return apiRequest<LinkedInStatus>(`${API_ENDPOINTS.LINKEDIN_STATUS}${query}`, {
        method: 'GET',
    });
}

/**
 * Initiate LinkedIn OAuth connection
 */
export async function connectLinkedIn(): Promise<LinkedInConnectResponse> {
    return apiRequest<LinkedInConnectResponse>(API_ENDPOINTS.LINKEDIN_CONNECT, {
        method: 'POST',
    });
}

/**
 * Disconnect LinkedIn account
 */
export async function disconnectLinkedIn(userId: string): Promise<LinkedInDisconnectResponse> {
    return apiRequest<LinkedInDisconnectResponse>(`${API_ENDPOINTS.LINKEDIN_DISCONNECT}?user_id=${userId}`, {
        method: 'POST',
    });
}
