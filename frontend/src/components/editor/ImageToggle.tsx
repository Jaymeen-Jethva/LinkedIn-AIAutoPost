// ============================================
// ImageToggle Component - Toggle for AI image generation
// ============================================

import { GlassCard } from '@/components/common';
import './ImageToggle.css';

interface ImageToggleProps {
    checked: boolean;
    onChange: (checked: boolean) => void;
}

export function ImageToggle({ checked, onChange }: ImageToggleProps) {
    return (
        <div className="form-group">
            <GlassCard style={{ padding: '1.25rem' }}>
                <label className="form-label" style={{ marginBottom: '1rem' }}>
                    Include AI Image
                </label>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <span style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
                        Generate stunning visuals
                    </span>
                    <label className="toggle-switch">
                        <input
                            type="checkbox"
                            checked={checked}
                            onChange={(e) => onChange(e.target.checked)}
                        />
                        <span className="toggle-track" />
                        <span className="toggle-thumb" />
                    </label>
                </div>
            </GlassCard>
        </div>
    );
}
