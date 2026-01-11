// ============================================
// TypeScript Types and Interfaces
// ============================================

// API Request Types
export interface PostRequest {
    topic: string;
    post_type: string;
    user_preferences: Record<string, string>;
    include_image: boolean;
    use_multi_agent: boolean;
}

export interface ApprovalRequest {
    session_id: string;
    approved: boolean;
    feedback?: string;
}

// API Response Types
export interface GeneratedPost {
    session_id: string;
    content: string;
    hashtags: string[];
    image_path?: string;
    image_prompt?: string;
}

export interface ApprovalResponse {
    success?: boolean;
    message?: string;
    revised?: boolean;
    content?: string;
    hashtags?: string[];
    image_path?: string;
    image_prompt?: string;
}

export interface LinkedInStatus {
    connected: boolean;
}

export interface LinkedInConnectResponse {
    authorization_url?: string;
    detail?: string;
}

export interface LinkedInDisconnectResponse {
    success: boolean;
    detail?: string;
}

// UI State Types
export type ToneType = 'professional' | 'viral' | 'story' | 'insightful' | 'direct';

export interface ToneOption {
    value: ToneType;
    label: string;
    emoji: string;
}

export const TONE_OPTIONS: ToneOption[] = [
    { value: 'professional', label: 'Professional', emoji: '👔' },
    { value: 'viral', label: 'Viral', emoji: '🚀' },
    { value: 'story', label: 'Story', emoji: '📖' },
    { value: 'insightful', label: 'Insightful', emoji: '💡' },
    { value: 'direct', label: 'Direct', emoji: '🎯' },
];

// Validation Constants
export const MIN_TOPIC_LENGTH = 10;
export const MAX_TOPIC_LENGTH = 500;
export const DANGEROUS_CHARS_PATTERN = /[<>{}|\\^`]/;
