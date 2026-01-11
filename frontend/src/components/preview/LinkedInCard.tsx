// ============================================
// LinkedInCard Component - LinkedIn post preview mockup
// ============================================

interface LinkedInCardProps {
    content: string;
    hashtags: string[];
    showImage: boolean;
    imagePath?: string;
}

export function LinkedInCard({ content, hashtags, showImage, imagePath }: LinkedInCardProps) {
    return (
        <div className="linkedin-card">
            {/* Card Header */}
            <div className="linkedin-card-header">
                <div className="linkedin-profile">
                    <div className="linkedin-avatar">JD</div>
                    <div className="linkedin-user-info">
                        <div className="linkedin-name">Your Name</div>
                        <div className="linkedin-meta">
                            <span>Your Title</span>
                            <span>•</span>
                            <span>Now</span>
                            <span>•</span>
                            <span>🌐</span>
                        </div>
                    </div>
                </div>
                <div className="linkedin-menu">⋯</div>
            </div>

            {/* Card Content */}
            <div className="linkedin-content">
                <div className="linkedin-text">{content}</div>

                {showImage && (
                    imagePath ? (
                        <img
                            src={`/images/${imagePath.split('/').pop()}`}
                            alt="Generated image"
                            style={{ width: '100%', borderRadius: '8px', marginBottom: '1rem' }}
                        />
                    ) : (
                        <div className="linkedin-image-placeholder" style={{ display: 'flex' }}>
                            <span>📸 Image will appear here</span>
                        </div>
                    )
                )}

                {hashtags.length > 0 && (
                    <div className="linkedin-hashtags">
                        {hashtags.map((tag, index) => (
                            <span key={index} className="linkedin-hashtag">
                                {tag}
                            </span>
                        ))}
                    </div>
                )}
            </div>

            {/* Card Footer */}
            <div className="linkedin-footer">
                <button className="linkedin-action">
                    <span className="action-icon">👍</span>
                    <span>Like</span>
                </button>
                <button className="linkedin-action">
                    <span className="action-icon">💬</span>
                    <span>Comment</span>
                </button>
                <button className="linkedin-action">
                    <span className="action-icon">🔄</span>
                    <span>Repost</span>
                </button>
                <button className="linkedin-action">
                    <span className="action-icon">📤</span>
                    <span>Send</span>
                </button>
            </div>
        </div>
    );
}
