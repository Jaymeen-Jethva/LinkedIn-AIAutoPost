// ============================================
// PreferencesInput Component - Optional preferences textarea
// ============================================

interface PreferencesInputProps {
    value: string;
    onChange: (value: string) => void;
}

export function PreferencesInput({ value, onChange }: PreferencesInputProps) {
    return (
        <div className="form-group">
            <label htmlFor="preferences" className="form-label">
                Additional Preferences (Optional)
            </label>
            <textarea
                className="prompter-input"
                id="preferences"
                name="preferences"
                rows={2}
                style={{ minHeight: '80px' }}
                placeholder="e.g., 'Keep it professional but friendly' or 'Include technical details'"
                value={value}
                onChange={(e) => onChange(e.target.value)}
            />
        </div>
    );
}
