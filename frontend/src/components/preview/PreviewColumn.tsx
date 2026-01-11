// ============================================
// PreviewColumn Component - Right column with live preview
// ============================================

import { useMemo } from 'react';
import { LinkedInCard } from './LinkedInCard';
import type { ToneType } from '@/types';

interface PreviewColumnProps {
    topic: string;
    tone: ToneType;
    preferences: string;
    includeImage: boolean;
}

export function PreviewColumn({ topic, tone, preferences, includeImage }: PreviewColumnProps) {
    // Generate mock content based on inputs
    const { content, hashtags } = useMemo(() => {
        if (topic.length < 10) {
            return {
                content:
                    'Your generated LinkedIn post will appear here. Fill out the form and click "Generate Post" to see your AI-powered content come to life! ✨',
                hashtags: [],
            };
        }

        const templates: Record<ToneType, string[]> = {
            professional: [
                `Exciting developments in ${topic}! The latest insights are reshaping how we approach this field. Here are the key takeaways every professional should know. 🎯`,
            ],
            viral: [
                `🚀 ${topic} is about to EXPLODE! Here's the insider perspective everyone needs to hear...`,
            ],
            story: [
                `Let me share a story about ${topic}. It started when I first discovered this fascinating field...`,
            ],
            insightful: [
                `After analyzing ${topic} for months, here are the patterns nobody's talking about 💡`,
            ],
            direct: [`${topic}: Here's what matters. No fluff, just facts. 🎯`],
        };

        let mockContent = templates[tone][0];
        if (preferences) {
            mockContent += `\n\n(Note: ${preferences})`;
        }

        // Generate hashtags from topic
        const baseHashtags = ['#LinkedIn', '#Professional', '#Growth'];
        const words = topic
            .toLowerCase()
            .split(' ')
            .filter((w) => w.length > 3);
        const topicHashtags = words.slice(0, 3).map((w) => `#${w.charAt(0).toUpperCase() + w.slice(1)}`);

        return {
            content: mockContent,
            hashtags: [...baseHashtags, ...topicHashtags].slice(0, 6),
        };
    }, [topic, tone, preferences]);

    return (
        <section className="preview-column">
            <div className="preview-header">
                <h2 className="preview-title">Live Preview</h2>
                <span className="preview-badge">Preview Mode</span>
            </div>

            <LinkedInCard
                content={content}
                hashtags={hashtags}
                showImage={includeImage}
            />
        </section>
    );
}
