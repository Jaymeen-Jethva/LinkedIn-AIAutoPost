// ============================================
// Snackbar Component - Toast notifications
// ============================================

import type { SnackbarMessage } from '@/hooks/useSnackbar';
import './Snackbar.css';

interface SnackbarProps {
    messages: SnackbarMessage[];
    onDismiss: (id: string) => void;
}

export function Snackbar({ messages, onDismiss }: SnackbarProps) {
    if (messages.length === 0) return null;

    return (
        <div className="snackbar-container">
            {messages.map((msg) => (
                <div
                    key={msg.id}
                    className="snackbar"
                    onClick={() => onDismiss(msg.id)}
                >
                    {msg.message}
                </div>
            ))}
        </div>
    );
}
