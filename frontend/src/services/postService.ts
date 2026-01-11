// ============================================
// Post Service - API calls for post generation
// ============================================

import { apiRequest, API_ENDPOINTS } from '@/config/api';
import type { PostRequest, GeneratedPost, ApprovalRequest, ApprovalResponse } from '@/types';

/**
 * Generate a new LinkedIn post
 */
export async function generatePost(request: PostRequest): Promise<GeneratedPost> {
    return apiRequest<GeneratedPost>(API_ENDPOINTS.GENERATE_POST, {
        method: 'POST',
        body: JSON.stringify(request),
    });
}

/**
 * Approve or request revision for a generated post
 */
export async function approvePost(
    sessionId: string,
    approved: boolean,
    feedback?: string
): Promise<ApprovalResponse> {
    const request: ApprovalRequest = {
        session_id: sessionId,
        approved,
        feedback,
    };

    return apiRequest<ApprovalResponse>(API_ENDPOINTS.APPROVE_POST, {
        method: 'POST',
        body: JSON.stringify(request),
    });
}
