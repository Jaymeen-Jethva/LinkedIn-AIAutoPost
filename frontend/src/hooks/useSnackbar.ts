// ============================================
// Snackbar Hook - Toast notification system
// ============================================

import { useState, useCallback } from 'react';

export interface SnackbarMessage {
    id: string;
    message: string;
}

export function useSnackbar() {
    const [messages, setMessages] = useState<SnackbarMessage[]>([]);

    const showSnackbar = useCallback((message: string, duration: number = 4000) => {
        const id = crypto.randomUUID();

        setMessages((prev) => [...prev, { id, message }]);

        setTimeout(() => {
            setMessages((prev) => prev.filter((msg) => msg.id !== id));
        }, duration);
    }, []);

    const dismissSnackbar = useCallback((id: string) => {
        setMessages((prev) => prev.filter((msg) => msg.id !== id));
    }, []);

    return {
        messages,
        showSnackbar,
        dismissSnackbar,
    };
}
