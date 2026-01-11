// ============================================
// TopicInput Component - Topic text area with counter
// ============================================

import { MAX_TOPIC_LENGTH } from '@/types';

interface TopicInputProps {
    value: string;
    onChange: (value: string) => void;
}

export function TopicInput({ value, onChange }: TopicInputProps) {
    const charCount = value.length;

    const getCounterColor = () => {
        if (charCount > MAX_TOPIC_LENGTH * 0.9) return 'var(--danger)';
        if (charCount > MAX_TOPIC_LENGTH * 0.7) return 'var(--warning)';
        return 'var(--text-dim)';
    };

    return (
        <div className="form-group">
            <label htmlFor="topic" className="form-label">
                What would you like to post about?
            </label>
            <textarea
                className="prompter-input"
                id="topic"
                name="topic"
                rows={5}
                placeholder="e.g., 'Latest developments in AI and machine learning' or 'I just completed my certification in data science'"
                value={value}
                onChange={(e) => onChange(e.target.value)}
                required
            />
            <div
                style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    marginTop: '0.5rem',
                    fontSize: '0.75rem',
                    color: 'var(--text-dim)',
                    fontFamily: "'JetBrains Mono', monospace",
                }}
            >
                <span style={{ color: getCounterColor() }}>{charCount}</span>
                <span>characters</span>
            </div>
        </div>
    );
}
