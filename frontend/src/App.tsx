// ============================================
// Main App Component
// ============================================

import { useState } from 'react';
import { Sidebar } from '@/components/layout';
import {
    TopicInput,
    TonePillSelector,
    ImageToggle,
    MultiAgentToggle,
    PreferencesInput,
    LinkedInStatus,
} from '@/components/editor';
import { PreviewColumn, PreviewModal } from '@/components/preview';
import { Snackbar, Spinner } from '@/components/common';
import { useSnackbar } from '@/hooks/useSnackbar';
import { generatePost, approvePost } from '@/services/postService';
import { validateTopic } from '@/utils/validation';
import type { ToneType, GeneratedPost } from '@/types';

import './index.css';

function App() {
    // Form state
    const [topic, setTopic] = useState('');
    const [tone, setTone] = useState<ToneType>('professional');
    const [includeImage, setIncludeImage] = useState(true);
    const [useMultiAgent, setUseMultiAgent] = useState(false);
    const [preferences, setPreferences] = useState('');

    // UI state
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [currentPost, setCurrentPost] = useState<GeneratedPost | null>(null);
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [isModalLoading, setIsModalLoading] = useState(false);

    // Snackbar
    const { messages, showSnackbar, dismissSnackbar } = useSnackbar();

    // Handle form submission
    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError(null);

        // Validate topic
        const validation = validateTopic(topic);
        if (!validation.isValid) {
            setError(validation.error!);
            return;
        }

        setIsLoading(true);

        try {
            const result = await generatePost({
                topic: topic.trim(),
                // TODO: Currently hardcoded to 'ai_news' - update when backend supports custom tone types
                post_type: 'ai_news',
                user_preferences: preferences ? { general: preferences } : {},
                include_image: includeImage,
                use_multi_agent: useMultiAgent,
            });

            setCurrentPost(result);
            setIsModalOpen(true);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Generation failed');
        } finally {
            setIsLoading(false);
        }
    };

    // Handle post approval
    const handleApprove = async () => {
        if (!currentPost) return;

        setIsModalLoading(true);
        try {
            const result = await approvePost(currentPost.session_id, true);
            if (result.success) {
                setIsModalOpen(false);
                showSnackbar('🎉 Post published successfully to LinkedIn!', 5000);
                // Reset form
                setTopic('');
                setPreferences('');
                setCurrentPost(null);
            } else {
                throw new Error(result.message || 'Posting failed');
            }
        } catch (err) {
            alert(err instanceof Error ? err.message : 'Posting failed');
        } finally {
            setIsModalLoading(false);
        }
    };

    // Handle revision request
    const handleRevise = async (feedback: string) => {
        if (!currentPost) return;

        setIsModalLoading(true);
        try {
            const result = await approvePost(currentPost.session_id, false, feedback);
            if (result.revised) {
                setCurrentPost({
                    ...currentPost,
                    content: result.content || currentPost.content,
                    hashtags: result.hashtags || currentPost.hashtags,
                    image_path: result.image_path || currentPost.image_path,
                    image_prompt: result.image_prompt || currentPost.image_prompt,
                });
                showSnackbar('Content revised! Check the new draft.', 4000);
            } else {
                throw new Error('Revision failed');
            }
        } catch (err) {
            alert(err instanceof Error ? err.message : 'Revision failed');
        } finally {
            setIsModalLoading(false);
        }
    };

    return (
        <>
            {/* Animated Gradient Orbs Background */}
            <div className="orb-container">
                <div className="orb orb-1"></div>
                <div className="orb orb-2"></div>
                <div className="orb orb-3"></div>
            </div>

            {/* Main App Container */}
            <div className="app-container">
                <Sidebar />

                <main className="main-content">
                    {/* Editor Column */}
                    <section className="editor-column">
                        <div className="editor-header">
                            <h1 className="editor-title">Create Your LinkedIn Post</h1>
                            <p className="editor-subtitle">Generate AI-powered content with stunning visuals</p>
                        </div>

                        <LinkedInStatus showSnackbar={showSnackbar} />

                        <form onSubmit={handleSubmit}>
                            <TopicInput value={topic} onChange={setTopic} />
                            <TonePillSelector value={tone} onChange={setTone} />
                            <ImageToggle checked={includeImage} onChange={setIncludeImage} />
                            <MultiAgentToggle checked={useMultiAgent} onChange={setUseMultiAgent} />
                            <PreferencesInput value={preferences} onChange={setPreferences} />

                            {/* Loading State */}
                            {isLoading && (
                                <Spinner
                                    message="Generating your post..."
                                    subMessage="This usually takes 10-30 seconds"
                                />
                            )}

                            {/* Error Alert */}
                            {error && (
                                <div
                                    className="alert alert-danger"
                                    style={{ marginBottom: '1.5rem' }}
                                >
                                    {error}
                                </div>
                            )}

                            {/* Submit Button */}
                            <button
                                type="submit"
                                className="magic-button"
                                disabled={isLoading}
                            >
                                ✨ Generate Post
                            </button>
                        </form>
                    </section>

                    {/* Preview Column */}
                    <PreviewColumn
                        topic={topic}
                        tone={tone}
                        preferences={preferences}
                        includeImage={includeImage}
                    />
                </main>
            </div>

            {/* Preview Modal */}
            <PreviewModal
                isOpen={isModalOpen}
                post={currentPost}
                onClose={() => setIsModalOpen(false)}
                onApprove={handleApprove}
                onRevise={handleRevise}
                isLoading={isModalLoading}
            />

            {/* Snackbar Notifications */}
            <Snackbar messages={messages} onDismiss={dismissSnackbar} />
        </>
    );
}

export default App;
