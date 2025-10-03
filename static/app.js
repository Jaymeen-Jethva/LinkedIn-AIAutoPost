// Theme Management
class ThemeManager {
    constructor() {
        this.theme = localStorage.getItem('theme') || 'dark'; // Default to dark for tech theme
        this.init();
    }

    init() {
        // Set initial theme
        document.documentElement.setAttribute('data-theme', this.theme);
        this.updateToggleIcon();

        // Create and setup toggle button
        this.createToggleButton();

        // Listen for system theme changes
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
            if (!localStorage.getItem('theme')) {
                this.setTheme(e.matches ? 'dark' : 'light');
            }
        });
    }

    createToggleButton() {
        const toggle = document.createElement('button');
        toggle.className = 'theme-toggle';
        toggle.setAttribute('data-theme', this.theme);
        toggle.setAttribute('aria-label', 'Toggle theme');
        toggle.innerHTML = `
            <div class="theme-toggle-slider">
                <svg class="theme-toggle-icon sun" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M12 2.25a.75.75 0 01.75.75v2.25a.75.75 0 01-1.5 0V3a.75.75 0 01.75-.75zM7.5 12a4.5 4.5 0 119 0 4.5 4.5 0 01-9 0zM18.894 6.166a.75.75 0 00-1.06-1.06l-1.591 1.59a.75.75 0 101.06 1.061l1.591-1.59zM21.75 12a.75.75 0 01-.75.75h-2.25a.75.75 0 010-1.5H21a.75.75 0 01.75.75zM17.834 18.894a.75.75 0 001.06-1.06l-1.59-1.591a.75.75 0 10-1.061 1.06l1.59 1.591zM12 18a.75.75 0 01.75.75V21a.75.75 0 01-1.5 0v-2.25A.75.75 0 0112 18zM7.758 17.303a.75.75 0 00-1.061-1.06l-1.591 1.59a.75.75 0 001.06 1.061l1.591-1.59zM6 12a.75.75 0 01-.75.75H3a.75.75 0 010-1.5h2.25A.75.75 0 016 12zM6.697 7.757a.75.75 0 001.06-1.06l-1.59-1.591a.75.75 0 00-1.061 1.06l1.59 1.591z" fill="currentColor"/>
                </svg>
                <svg class="theme-toggle-icon moon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M9.528 1.718a.75.75 0 01.162.819A8.97 8.97 0 009 6a9 9 0 009 9 8.97 8.97 0 003.463-.69.75.75 0 01.981.98 10.503 10.503 0 01-9.694 6.46c-5.799 0-10.5-4.701-10.5-10.5 0-4.368 2.667-8.112 6.46-9.694a.75.75 0 01.818.162z" fill="currentColor"/>
                </svg>
            </div>
        `;
        toggle.addEventListener('click', () => this.toggleTheme());
        document.body.appendChild(toggle);
    }

    setTheme(theme) {
        this.theme = theme;
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('theme', theme);
        this.updateToggleIcon();
    }

    toggleTheme() {
        this.setTheme(this.theme === 'light' ? 'dark' : 'light');
    }

    updateToggleIcon() {
        const toggle = document.querySelector('.theme-toggle');
        if (!toggle) return;

        // Update the data-theme attribute on the toggle button
        toggle.setAttribute('data-theme', this.theme);
    }
}

// Character Counter
class CharacterCounter {
    constructor(textareaId, counterId, progressId) {
        this.textarea = document.getElementById(textareaId);
        this.counter = document.getElementById(counterId);
        this.progress = document.getElementById(progressId);
        this.maxLength = 3000; // LinkedIn character limit

        this.init();
    }

    init() {
        if (this.textarea) {
            this.textarea.addEventListener('input', () => this.update());
            this.update();
        }
    }

    update() {
        const length = this.textarea.value.length;
        this.counter.textContent = length;

        // Update progress ring
        const percentage = Math.min((length / this.maxLength) * 100, 100);
        const circumference = 2 * Math.PI * 14; // radius = 14
        const strokeDasharray = (percentage / 100) * circumference;

        this.progress.style.strokeDasharray = `${strokeDasharray} ${circumference}`;

        // Color coding
        if (percentage > 90) {
            this.progress.style.stroke = 'var(--danger-color)';
        } else if (percentage > 70) {
            this.progress.style.stroke = 'var(--warning-color)';
        } else {
            this.progress.style.stroke = 'var(--primary-color)';
        }
    }
}

// Segmented Controls
class SegmentedControl {
    constructor(containerId, hiddenInputId) {
        this.container = document.getElementById(containerId);
        this.hiddenInput = document.getElementById(hiddenInputId);
        this.buttons = this.container.querySelectorAll('button');

        this.init();
    }

    init() {
        this.buttons.forEach(button => {
            button.addEventListener('click', () => this.select(button));
        });
    }

    select(selectedButton) {
        // Remove active class from all buttons
        this.buttons.forEach(btn => btn.classList.remove('active'));

        // Add active class to selected button
        selectedButton.classList.add('active');

        // Update hidden input
        const value = selectedButton.getAttribute('data-value');
        this.hiddenInput.value = value;
    }
}

// Advanced Options Accordion
class AdvancedOptions {
    constructor(toggleId, contentId) {
        this.toggle = document.getElementById(toggleId);
        this.content = document.getElementById(contentId);
        this.isExpanded = false;

        this.init();
    }

    init() {
        if (this.toggle) {
            this.toggle.addEventListener('click', () => this.toggleAccordion());
        }
    }

    toggleAccordion() {
        this.isExpanded = !this.isExpanded;

        this.toggle.classList.toggle('expanded', this.isExpanded);
        this.content.classList.toggle('expanded', this.isExpanded);
    }
}

// Live Preview
class LivePreview {
    constructor(previewId) {
        this.preview = document.getElementById(previewId);
        this.currentContent = null;

        this.init();
    }

    init() {
        // Listen for form changes to update preview
        this.setupFormListeners();
    }

    setupFormListeners() {
        const topicTextarea = document.getElementById('topic');
        const postTypeInput = document.getElementById('post_type');

        if (topicTextarea) {
            topicTextarea.addEventListener('input', () => this.updatePreview());
        }

        if (postTypeInput) {
            postTypeInput.addEventListener('change', () => this.updatePreview());
        }
    }

    updatePreview() {
        const topic = document.getElementById('topic')?.value || '';
        const postType = document.getElementById('post_type')?.value || 'ai_news';

        if (topic.length > 10) {
            this.showGeneratedPreview(topic, postType);
        } else {
            this.showPlaceholder();
        }
    }

    showPlaceholder() {
        this.preview.innerHTML = `
            <div class="preview-placeholder">
                <div style="font-size: 2rem; margin-bottom: 1rem;">✨</div>
                <p>Your generated LinkedIn post will appear here</p>
                <p style="font-size: 0.875rem; opacity: 0.7;">Fill out the form and watch it update in real-time</p>
            </div>
        `;
    }

    showGeneratedPreview(topic, postType) {
        // Simulate AI-generated content based on input
        const mockContent = this.generateMockContent(topic, postType);
        const mockHashtags = this.generateMockHashtags(topic);

        this.preview.innerHTML = `
            <div class="glass-card" style="padding: 1.5rem;">
                <div style="margin-bottom: 1rem;">
                    <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                        <div style="width: 40px; height: 40px; background: var(--primary-color); border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold;">JD</div>
                        <div>
                            <div style="font-weight: 600; font-size: 0.875rem;">John Doe</div>
                            <div style="font-size: 0.75rem; color: var(--text-muted);">Software Engineer • 1h</div>
                        </div>
                    </div>
                </div>

                <div style="margin-bottom: 1rem; line-height: 1.6;">
                    ${mockContent}
                </div>

                <div style="margin-bottom: 1rem;">
                    <div class="skeleton skeleton-image" style="height: 200px; border-radius: 12px;"></div>
                </div>

                <div style="display: flex; flex-wrap: wrap; gap: 0.5rem;">
                    ${mockHashtags.map(tag => `<span class="badge bg-primary">${tag}</span>`).join('')}
                </div>

                <div style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid var(--border-color); display: flex; justify-content: space-between; align-items: center;">
                    <div style="display: flex; gap: 1rem; font-size: 0.875rem; color: var(--text-muted);">
                        <span>👍 42</span>
                        <span>💬 8 comments</span>
                        <span>🔄 3 reposts</span>
                    </div>
                    <div style="font-size: 0.75rem; color: var(--text-muted);">
                        Live Preview
                    </div>
                </div>
            </div>
        `;
    }

    generateMockContent(topic, postType) {
        const templates = {
            ai_news: [
                `Exciting developments in ${topic}! The latest breakthroughs are pushing boundaries and opening new possibilities. What are your thoughts on this emerging trend? 🤔`,
                `Just read about the latest in ${topic}. The innovation happening here is incredible. Here's what caught my attention...`,
                `The ${topic} landscape is evolving rapidly. Here are the key insights from recent developments that every tech professional should know.`
            ],
            personal_milestone: [
                `Today marks an important milestone in my journey with ${topic}. Grateful for the opportunities and excited for what's next! 🚀`,
                `Reflecting on my experience with ${topic}. The lessons learned and growth achieved have been invaluable. Here's what I've discovered...`,
                `Celebrating progress in ${topic}! Sometimes the journey teaches us more than the destination. Here's my latest chapter.`
            ],
            engaging: [
                `What's your take on ${topic}? I'd love to hear different perspectives from the community. Share your thoughts below! 👇`,
                `The conversation around ${topic} is fascinating. Here are my current thoughts, but I'm curious about yours...`,
                `Let's discuss ${topic}! What trends are you noticing? What challenges are you facing? Looking forward to your insights.`
            ]
        };

        const templateList = templates[postType] || templates.ai_news;
        return templateList[Math.floor(Math.random() * templateList.length)];
    }

    generateMockHashtags(topic) {
        const baseHashtags = ['#Tech', '#Innovation', '#FutureOfWork'];
        const topicWords = topic.toLowerCase().split(' ').filter(word => word.length > 3);
        const topicHashtags = topicWords.map(word => `#${word.charAt(0).toUpperCase() + word.slice(1)}`);

        return [...baseHashtags, ...topicHashtags.slice(0, 3)];
    }
}

// Snackbar Notifications
class Snackbar {
    constructor() {
        this.container = null;
        this.init();
    }

    init() {
        // Create container if it doesn't exist
        if (!document.querySelector('.snackbar-container')) {
            this.container = document.createElement('div');
            this.container.className = 'snackbar-container';
            document.body.appendChild(this.container);
        } else {
            this.container = document.querySelector('.snackbar-container');
        }
    }

    show(message, actions = [], duration = 4000) {
        const snackbar = document.createElement('div');
        snackbar.className = 'snackbar';

        snackbar.innerHTML = `
            <div class="snackbar-message">${message}</div>
            ${actions.length > 0 ? `
                <div class="snackbar-actions">
                    ${actions.map(action => `<button class="btn btn-sm btn-primary" onclick="${action.callback}">${action.label}</button>`).join('')}
                </div>
            ` : ''}
        `;

        this.container.appendChild(snackbar);

        // Auto-hide after duration
        setTimeout(() => {
            snackbar.classList.add('hide');
            setTimeout(() => {
                if (snackbar.parentNode) {
                    snackbar.parentNode.removeChild(snackbar);
                }
            }, 300);
        }, duration);
    }
}

// Form Handling
class PostForm {
    constructor() {
        this.form = document.getElementById('postForm');
        this.loadingContainer = document.getElementById('loading');
        this.errorAlert = document.getElementById('error');
        this.currentSessionId = null;
        this.snackbar = new Snackbar();

        this.init();
    }

    init() {
        if (this.form) {
            this.form.addEventListener('submit', (e) => this.handleSubmit(e));
        }

        // Setup modal buttons
        this.setupModalButtons();
    }

    async handleSubmit(e) {
        e.preventDefault();

        const formData = new FormData(e.target);
        const preferences = formData.get('preferences');

        const postData = {
            topic: formData.get('topic'),
            post_type: formData.get('post_type'),
            user_preferences: preferences ? {general: preferences} : {}
        };

        this.showLoading(true);
        this.hideError();

        try {
            const response = await fetch('/generate-post', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(postData)
            });

            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.detail || 'Generation failed');
            }

            this.currentSessionId = result.session_id;
            this.showPreview(result);

        } catch (error) {
            this.showError(error.message);
        } finally {
            this.showLoading(false);
        }
    }

    showPreview(data) {
        const previewHtml = `
            <div class="card">
                <div class="card-body">
                    <h6 class="card-subtitle mb-2 text-muted">Generated Content:</h6>
                    <p class="card-text">${data.content.replace(/\n/g, '<br>')}</p>

                    <h6 class="card-subtitle mb-2 text-muted mt-3">Hashtags:</h6>
                    <p class="card-text">
                        ${data.hashtags.map(tag => `<span class="badge bg-primary me-1">${tag}</span>`).join('')}
                    </p>

                    ${data.image_path ? `
                        <h6 class="card-subtitle mb-2 text-muted mt-3">Generated Image:</h6>
                        <img src="/images/${data.image_path.split('/').pop()}" class="img-fluid rounded" alt="Generated image">
                    ` : `
                        <h6 class="card-subtitle mb-2 text-muted mt-3">Image Prompt:</h6>
                        <p class="card-text text-muted">${data.image_prompt}</p>
                        <p class="text-warning"><small>⚠️ Image generation failed, but will be retried if you approve.</small></p>
                    `}
                </div>
            </div>
        `;

        document.getElementById('postPreview').innerHTML = previewHtml;
        new bootstrap.Modal(document.getElementById('previewModal')).show();
    }

    setupModalButtons() {
        // Approve button
        const approveBtn = document.getElementById('approveBtn');
        if (approveBtn) {
            approveBtn.addEventListener('click', async () => {
                if (!this.currentSessionId) return;

                try {
                    const response = await fetch('/approve-post', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({
                            session_id: this.currentSessionId,
                            approved: true
                        })
                    });

                    const result = await response.json();

                    if (result.success) {
                        alert('🎉 Your post has been successfully posted to LinkedIn!');
                        location.reload();
                    } else {
                        throw new Error(result.message || 'Posting failed');
                    }

                } catch (error) {
                    alert('Error: ' + error.message);
                }
            });
        }

        // Revise button
        const reviseBtn = document.getElementById('reviseBtn');
        if (reviseBtn) {
            reviseBtn.addEventListener('click', () => {
                bootstrap.Modal.getInstance(document.getElementById('previewModal')).hide();
                new bootstrap.Modal(document.getElementById('revisionModal')).show();
            });
        }

        // Submit revision button
        const submitRevision = document.getElementById('submitRevision');
        if (submitRevision) {
            submitRevision.addEventListener('click', async () => {
                const feedback = document.getElementById('feedbackText').value.trim();

                if (!feedback) {
                    alert('Please provide specific feedback for revision.');
                    return;
                }

                if (!this.currentSessionId) return;

                try {
                    const response = await fetch('/approve-post', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({
                            session_id: this.currentSessionId,
                            approved: false,
                            feedback: feedback
                        })
                    });

                    const result = await response.json();

                    if (result.revised) {
                        bootstrap.Modal.getInstance(document.getElementById('revisionModal')).hide();
                        this.showPreview(result);
                        document.getElementById('feedbackText').value = '';
                    } else {
                        throw new Error('Revision failed');
                    }

                } catch (error) {
                    alert('Error: ' + error.message);
                }
            });
        }
    }

    showLoading(show) {
        if (this.loadingContainer) {
            this.loadingContainer.style.display = show ? 'block' : 'none';
        }
        const submitBtn = this.form?.querySelector('button[type="submit"]');
        if (submitBtn) {
            submitBtn.disabled = show;
        }
    }

    showError(message) {
        if (this.errorAlert) {
            this.errorAlert.textContent = message;
            this.errorAlert.style.display = 'block';
        }
    }

    hideError() {
        if (this.errorAlert) {
            this.errorAlert.style.display = 'none';
        }
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Initialize all components
    new ThemeManager();
    new CharacterCounter('topic', 'charCount', 'progressCircle');
    new SegmentedControl('postTypeControl', 'post_type');
    new AdvancedOptions('advancedToggle', 'advancedContent');
    new LivePreview('previewContent');
    new PostForm();
});
