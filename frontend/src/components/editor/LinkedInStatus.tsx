// ============================================
// LinkedInStatus Component - Connection status UI
// ============================================

import { useState, useEffect } from 'react';
import { GlassCard } from '@/components/common';
import { getLinkedInStatus, connectLinkedIn, disconnectLinkedIn } from '@/services/linkedInService';

interface LinkedInStatusProps {
    showSnackbar: (message: string, duration?: number) => void;
}

export function LinkedInStatus({ showSnackbar }: LinkedInStatusProps) {
    const [isConnected, setIsConnected] = useState(false);
    const [isLoading, setIsLoading] = useState(false);

    useEffect(() => {
        checkStatus();
        handleOAuthRedirect();
    }, []);

    const checkStatus = async () => {
        try {
            const userId = localStorage.getItem('user_id');
            // If no user_id, we can't be connected in this implementation
            if (!userId) {
                setIsConnected(false);
                return;
            }
            const status = await getLinkedInStatus(userId);
            setIsConnected(status.connected);
        } catch (error) {
            console.error('Failed to check LinkedIn status:', error);
            setIsConnected(false);
        }
    };

    const handleOAuthRedirect = () => {
        const urlParams = new URLSearchParams(window.location.search);

        if (urlParams.has('linkedin_connected')) {
            const userId = urlParams.get('user_id');
            if (userId) {
                localStorage.setItem('user_id', userId);
            }
            showSnackbar('✅ Successfully connected to LinkedIn!', 5000);
            window.history.replaceState({}, document.title, window.location.pathname);
            checkStatus();
        }

        if (urlParams.has('linkedin_error')) {
            const error = urlParams.get('linkedin_error');
            showSnackbar(`❌ LinkedIn connection failed: ${error}`, 6000);
            window.history.replaceState({}, document.title, window.location.pathname);
        }
    };

    const handleConnect = async () => {
        setIsLoading(true);
        try {
            const response = await connectLinkedIn();
            if (response.authorization_url) {
                window.location.href = response.authorization_url;
            } else {
                throw new Error(response.detail || 'Failed to get authorization URL');
            }
        } catch (error) {
            showSnackbar(`❌ ${error instanceof Error ? error.message : 'Connection failed'}`, 5000);
            setIsLoading(false);
        }
    };

    const handleDisconnect = async () => {
        if (!confirm('Are you sure you want to disconnect LinkedIn?')) {
            return;
        }

        setIsLoading(true);
        try {
            const userId = localStorage.getItem('user_id');
            if (!userId) {
                throw new Error('User ID not found');
            }
            const response = await disconnectLinkedIn(userId);
            if (response.success) {
                localStorage.removeItem('user_id');
                showSnackbar('✅ Disconnected from LinkedIn', 4000);
                setIsConnected(false);
            } else {
                throw new Error(response.detail || 'Disconnect failed');
            }
        } catch (error) {
            showSnackbar(`❌ ${error instanceof Error ? error.message : 'Disconnect failed'}`, 5000);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <GlassCard className="mb-3" style={{ padding: '1rem' }}>
            {isConnected ? (
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <span style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>LinkedIn</span>
                        <span
                            style={{
                                width: '8px',
                                height: '8px',
                                background: 'var(--success)',
                                borderRadius: '50%',
                                boxShadow: '0 0 8px var(--success)',
                            }}
                        />
                    </div>
                    <button
                        onClick={handleDisconnect}
                        disabled={isLoading}
                        style={{
                            padding: '0.5rem 1rem',
                            background: 'transparent',
                            border: '1px solid var(--glass-border)',
                            borderRadius: '8px',
                            color: 'var(--text-muted)',
                            fontSize: '0.875rem',
                            cursor: isLoading ? 'wait' : 'pointer',
                        }}
                    >
                        {isLoading ? '...' : 'Disconnect'}
                    </button>
                </div>
            ) : (
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <span style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>LinkedIn</span>
                        <span
                            style={{
                                width: '8px',
                                height: '8px',
                                background: 'var(--text-dim)',
                                borderRadius: '50%',
                            }}
                        />
                    </div>
                    <button
                        onClick={handleConnect}
                        disabled={isLoading}
                        style={{
                            padding: '0.5rem 1rem',
                            background: 'linear-gradient(135deg, #0077b5, #0a66c2)',
                            border: 'none',
                            borderRadius: '8px',
                            color: 'white',
                            fontSize: '0.875rem',
                            fontWeight: 600,
                            cursor: isLoading ? 'wait' : 'pointer',
                        }}
                    >
                        {isLoading ? '...' : 'Connect'}
                    </button>
                </div>
            )}
        </GlassCard>
    );
}
