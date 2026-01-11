// ============================================
// Spinner Component - Loading indicator
// ============================================

interface SpinnerProps {
    message?: string;
    subMessage?: string;
}

export function Spinner({ message = 'Loading...', subMessage }: SpinnerProps) {
    return (
        <div className="loading-container active">
            <div className="spinner"></div>
            <p style={{ color: 'var(--text-secondary)', fontWeight: 600, marginBottom: '0.5rem' }}>
                {message}
            </p>
            {subMessage && (
                <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>
                    {subMessage}
                </p>
            )}
        </div>
    );
}
