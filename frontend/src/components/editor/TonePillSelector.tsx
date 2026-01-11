// ============================================
// TonePillSelector Component - Tone selection UI
// ============================================

import { TONE_OPTIONS, type ToneType } from '@/types';

interface TonePillSelectorProps {
    value: ToneType;
    onChange: (tone: ToneType) => void;
}

export function TonePillSelector({ value, onChange }: TonePillSelectorProps) {
    return (
        <div className="form-group">
            <label className="form-label">Select Tone</label>
            <div className="tone-pills-container">
                {TONE_OPTIONS.map((option) => (
                    <div
                        key={option.value}
                        className={`tone-pill ${value === option.value ? 'active' : ''}`}
                        onClick={() => onChange(option.value)}
                    >
                        <span className="tone-pill-emoji">{option.emoji}</span>
                        <span>{option.label}</span>
                    </div>
                ))}
            </div>
        </div>
    );
}
