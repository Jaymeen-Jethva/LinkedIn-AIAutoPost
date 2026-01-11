// ============================================
// LinkedIn Service - OAuth and connection APIs
// ============================================

import { apiRequest, API_ENDPOINTS } from '@/config/api';
import type { LinkedInStatus, LinkedInConnectResponse, LinkedInDisconnectResponse } from '@/types';

/**
 * Check LinkedIn connection status
 */
export async function getLinkedInStatus(): Promise<LinkedInStatus> {
    return apiRequest<LinkedInStatus>(API_ENDPOINTS.LINKEDIN_STATUS, {
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
export async function disconnectLinkedIn(): Promise<LinkedInDisconnectResponse> {
    return apiRequest<LinkedInDisconnectResponse>(API_ENDPOINTS.LINKEDIN_DISCONNECT, {
        method: 'POST',
    });
}
