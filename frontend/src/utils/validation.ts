// ============================================
// Input Validation Utilities
// ============================================

import { MIN_TOPIC_LENGTH, MAX_TOPIC_LENGTH, DANGEROUS_CHARS_PATTERN } from '@/types';

export interface ValidationResult {
    isValid: boolean;
    error?: string;
}

/**
 * Validate topic input for length and dangerous characters
 */
export function validateTopic(topic: string): ValidationResult {
    const trimmedTopic = topic.trim();

    if (!trimmedTopic) {
        return {
            isValid: false,
            error: 'Please enter a topic for your post',
        };
    }

    if (trimmedTopic.length < MIN_TOPIC_LENGTH) {
        return {
            isValid: false,
            error: `Topic must be at least ${MIN_TOPIC_LENGTH} characters long (currently ${trimmedTopic.length})`,
        };
    }

    if (trimmedTopic.length > MAX_TOPIC_LENGTH) {
        return {
            isValid: false,
            error: `Topic must not exceed ${MAX_TOPIC_LENGTH} characters (currently ${trimmedTopic.length})`,
        };
    }

    if (DANGEROUS_CHARS_PATTERN.test(trimmedTopic)) {
        return {
            isValid: false,
            error: 'Topic contains invalid characters. Please remove: < > { } | \\ ^ `',
        };
    }

    return { isValid: true };
}
