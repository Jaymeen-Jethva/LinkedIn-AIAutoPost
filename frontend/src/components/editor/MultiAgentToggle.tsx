// ============================================
// MultiAgentToggle Component - Toggle for multi-agent AI system
// ============================================

import { GlassCard } from '@/components/common';
import './MultiAgentToggle.css';

interface MultiAgentToggleProps {
    checked: boolean;
    onChange: (checked: boolean) => void;
}

export function MultiAgentToggle({ checked, onChange }: MultiAgentToggleProps) {
    return (
        <div className="form-group">
            <GlassCard style={{ padding: '1.25rem' }}>
                <div className="multi-agent-header">
                    <label className="form-label" style={{ marginBottom: '0.5rem' }}>
                        <span className="multi-agent-label">
                            ✨ Multi-Agent AI
                            <span className="multi-agent-badge">Pro</span>
                        </span>
                    </label>
                </div>
                <p className="multi-agent-description">
                    6 specialized AI agents collaborate for higher quality content
                </p>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginTop: '0.75rem' }}>
                    <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                        {checked ? 'Research → Strategy → Write → Edit → SEO → Visual' : 'Standard single-agent generation'}
                    </span>
                    <label className="toggle-switch">
                        <input
                            type="checkbox"
                            checked={checked}
                            onChange={(e) => onChange(e.target.checked)}
                        />
                        <span className="toggle-track multi-agent-track" />
                        <span className="toggle-thumb" />
                    </label>
                </div>
            </GlassCard>
        </div>
    );
}
