// ============================================
// PreviewModal Component - Modal for reviewing generated post
// ============================================

import { useState } from 'react';
import { GlassCard } from '@/components/common';
import type { GeneratedPost } from '@/types';

interface PreviewModalProps {
    isOpen: boolean;
    post: GeneratedPost | null;
    onClose: () => void;
    onApprove: () => Promise<void>;
    onRevise: (feedback: string) => Promise<void>;
    isLoading: boolean;
}

export function PreviewModal({
    isOpen,
    post,
    onClose,
    onApprove,
    onRevise,
    isLoading,
}: PreviewModalProps) {
    const [showRevisionInput, setShowRevisionInput] = useState(false);
    const [feedback, setFeedback] = useState('');

    if (!isOpen || !post) return null;

    const handleApprove = async () => {
        await onApprove();
    };

    const handleRevise = async () => {
        if (!feedback.trim()) {
            alert('Please provide feedback');
            return;
        }
        await onRevise(feedback);
        setFeedback('');
        setShowRevisionInput(false);
    };

    return (
        <>
            {/* Backdrop */}
            <div
                className="modal-backdrop fade show"
                style={{ display: 'block' }}
                onClick={onClose}
            />

            {/* Modal */}
            <div
                className="modal fade show"
                style={{ display: 'block' }}
                tabIndex={-1}
            >
                <div className="modal-dialog modal-lg">
                    <div
                        className="modal-content"
                        style={{
                            background: 'var(--bg-secondary)',
                            border: '1px solid var(--glass-border)',
                            borderRadius: '16px',
                        }}
                    >
                        <div
                            className="modal-header"
                            style={{ borderBottom: '1px solid var(--glass-border)' }}
                        >
                            <h5 className="modal-title" style={{ color: 'var(--text-primary)' }}>
                                Review Your LinkedIn Post
                            </h5>
                            <button
                                type="button"
                                className="btn-close"
                                style={{ filter: 'invert(1)' }}
                                onClick={onClose}
                                disabled={isLoading}
                            />
                        </div>

                        <div className="modal-body" style={{ background: 'var(--bg-primary)' }}>
                            <GlassCard style={{ padding: '1.5rem' }}>
                                <h6
                                    style={{
                                        color: 'var(--text-muted)',
                                        fontSize: '0.875rem',
                                        marginBottom: '0.75rem',
                                    }}
                                >
                                    Generated Content:
                                </h6>
                                <p
                                    style={{
                                        color: 'var(--text-secondary)',
                                        lineHeight: 1.6,
                                        whiteSpace: 'pre-wrap',
                                    }}
                                    dangerouslySetInnerHTML={{
                                        __html: post.content.replace(/\n/g, '<br>'),
                                    }}
                                />

                                <h6
                                    style={{
                                        color: 'var(--text-muted)',
                                        fontSize: '0.875rem',
                                        marginTop: '1.5rem',
                                        marginBottom: '0.75rem',
                                    }}
                                >
                                    Hashtags:
                                </h6>
                                <p>
                                    {post.hashtags.map((tag, index) => (
                                        <span key={index} className="linkedin-hashtag" style={{ marginRight: '0.5rem' }}>
                                            {tag}
                                        </span>
                                    ))}
                                </p>

                                {post.image_path ? (
                                    <>
                                        <h6
                                            style={{
                                                color: 'var(--text-muted)',
                                                fontSize: '0.875rem',
                                                marginTop: '1.5rem',
                                                marginBottom: '0.75rem',
                                            }}
                                        >
                                            Generated Image:
                                        </h6>
                                        <img
                                            src={`/images/${post.image_path.split('/').pop()}`}
                                            alt="Generated image"
                                            style={{ width: '100%', borderRadius: '12px' }}
                                        />
                                    </>
                                ) : post.image_prompt ? (
                                    <>
                                        <h6
                                            style={{
                                                color: 'var(--text-muted)',
                                                fontSize: '0.875rem',
                                                marginTop: '1.5rem',
                                                marginBottom: '0.75rem',
                                            }}
                                        >
                                            Image Prompt:
                                        </h6>
                                        <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>
                                            {post.image_prompt}
                                        </p>
                                        <p style={{ color: 'var(--warning)', fontSize: '0.875rem' }}>
                                            ⚠️ Image generation failed, but will be retried if you approve.
                                        </p>
                                    </>
                                ) : null}
                            </GlassCard>

                            {/* Revision Input */}
                            {showRevisionInput && (
                                <div style={{ marginTop: '1rem' }}>
                                    <textarea
                                        className="prompter-input"
                                        rows={4}
                                        placeholder="What would you like to change? Be specific about your feedback..."
                                        value={feedback}
                                        onChange={(e) => setFeedback(e.target.value)}
                                    />
                                </div>
                            )}
                        </div>

                        <div
                            className="modal-footer"
                            style={{ borderTop: '1px solid var(--glass-border)' }}
                        >
                            <button
                                type="button"
                                className="btn btn-secondary"
                                onClick={onClose}
                                disabled={isLoading}
                            >
                                Cancel
                            </button>
                            {showRevisionInput ? (
                                <button
                                    type="button"
                                    className="btn btn-primary"
                                    onClick={handleRevise}
                                    disabled={isLoading}
                                >
                                    {isLoading ? 'Revising...' : 'Submit Revision Request'}
                                </button>
                            ) : (
                                <>
                                    <button
                                        type="button"
                                        className="btn btn-warning"
                                        onClick={() => setShowRevisionInput(true)}
                                        disabled={isLoading}
                                    >
                                        Request Revision
                                    </button>
                                    <button
                                        type="button"
                                        className="btn btn-success"
                                        onClick={handleApprove}
                                        disabled={isLoading}
                                    >
                                        {isLoading ? 'Posting...' : 'Approve & Post'}
                                    </button>
                                </>
                            )}
                        </div>
                    </div>
                </div>
            </div>
        </>
    );
}
