// Theme Management
class ThemeManager {
  constructor() {
    this.theme = localStorage.getItem('theme') || 'dark';
    this.init();
  }

  init() {
    document.documentElement.setAttribute('data-theme', this.theme);
    this.updateToggleUI();

    // Listen for system theme changes
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
      if (!localStorage.getItem('theme')) {
        this.setTheme(e.matches ? 'dark' : 'light');
      }
    });

    this.setupToggleClick();
  }

  setupToggleClick() {
    const toggle = document.querySelector('.theme-toggle');
    if (!toggle) return;
    toggle.addEventListener('click', () => this.toggleTheme());
  }

  toggleTheme() {
    const newTheme = this.theme === 'light' ? 'dark' : 'light';
    this.setTheme(newTheme);
  }

  setTheme(theme) {
    this.theme = theme;
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
    this.updateToggleUI();
  }

  updateToggleUI() {
    const toggle = document.querySelector('.theme-toggle');
    if (!toggle) return;
    toggle.setAttribute('data-theme', this.theme);
    // We will style the toggle slider in CSS based on [data-theme]
  }
}

// Character Counter
class CharacterCounter {
  constructor(textareaId, counterId, progressId) {
    this.textarea = document.getElementById(textareaId);
    this.counter = document.getElementById(counterId);
    this.progress = document.getElementById(progressId);
    this.maxLength = 3000;
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
    const percentage = Math.min((length / this.maxLength) * 100, 100);
    const circumference = 2 * Math.PI * 14;
    const strokeDasharray = (percentage / 100) * circumference;
    this.progress.style.strokeDasharray = `${strokeDasharray} ${circumference}`;

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
    this.buttons = this.container?.querySelectorAll('button') || [];
    this.init();
  }

  init() {
    this.buttons.forEach((button) => {
      button.addEventListener('click', () => this.select(button));
    });
  }

  select(selectedButton) {
    this.buttons.forEach((btn) => btn.classList.remove('active'));
    selectedButton.classList.add('active');
    const value = selectedButton.getAttribute('data-value');
    if (this.hiddenInput) {
      this.hiddenInput.value = value;
      this.hiddenInput.dispatchEvent(new Event('change'));
    }
  }
}

// Image Toggle Control
class ImageToggle {
  constructor(checkboxId) {
    this.checkbox = document.getElementById(checkboxId);
    this.init();
  }

  init() {
    if (this.checkbox) {
      this.checkbox.addEventListener('change', () => this.onToggle());
      this.updateVisual();
    }
  }

  onToggle() {
    this.updateVisual();
    // You can also trigger preview update or form signaling
    const evt = new Event('change');
    this.checkbox.dispatchEvent(evt);
  }

  updateVisual() {
    const container = this.checkbox.closest('.image-toggle-container');
    if (!container) return;
    if (this.checkbox.checked) {
      container.classList.add('image-enabled');
      container.classList.remove('image-disabled');
      container.querySelector('.toggle-desc-on')?.style.setProperty('display', 'inline');
      container.querySelector('.toggle-desc-off')?.style.setProperty('display', 'none');
    } else {
      container.classList.add('image-disabled');
      container.classList.remove('image-enabled');
      container.querySelector('.toggle-desc-on')?.style.setProperty('display', 'none');
      container.querySelector('.toggle-desc-off')?.style.setProperty('display', 'inline');
    }
  }
}


// Live Preview (same logic, minor tweaks)
class LivePreview {
  constructor(previewId) {
    this.preview = document.getElementById(previewId);
    this.init();
  }

  init() {
    this.setupListeners();
    this.showPlaceholder();
  }

  setupListeners() {
    const topic = document.getElementById('topic');
    const postType = document.getElementById('post_type');
    const imageToggle = document.getElementById('includeImageToggle');
    const preferencesInput = document.getElementById('preferences');

    topic?.addEventListener('input', () => this.updatePreview());
    postType?.addEventListener('change', () => this.updatePreview());
    imageToggle?.addEventListener('change', () => this.updatePreview());
    preferencesInput?.addEventListener('input', () => this.updatePreview());
  }

    updatePreview() {
        const topic = document.getElementById('topic')?.value || '';
        const postType = document.getElementById('post_type')?.value || 'ai_news';
        const preferences = document.getElementById('preferences')?.value || '';

        if (topic.length > 10) {
            this.showGeneratedPreview(topic, postType, preferences);
        } else {
            this.showPlaceholder();
        }
    }

    showSearchStatus(show) {
        const searchStatus = document.getElementById('searchStatus');
        if (searchStatus) {
            searchStatus.style.display = show ? 'flex' : 'none';
        }
    }

  showPlaceholder() {
    if (!this.preview) return;
    this.preview.innerHTML = `
      <div class="preview-placeholder">
        <div style="font-size: 2rem; margin-bottom: 1rem;">✨</div>
        <p>Your generated LinkedIn post will appear here</p>
        <p style="font-size: 0.875rem; opacity: 0.7;">Fill out the form and watch it update in real-time</p>
      </div>
    `;
  }

  showGeneratedPreview(topic, postType, preferences) {
    if (!this.preview) return;
    const mockContent = this.generateMockContent(topic, postType, preferences);
    const mockHashtags = this.generateMockHashtags(topic);
    const includeImage = document.getElementById('includeImageToggle')?.checked ?? true;

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

        ${includeImage
          ? `<div style="margin-bottom: 1rem;">
              <div class="skeleton skeleton-image" style="height: 200px; border-radius: 12px;"></div>
            </div>`
          : `<div style="margin-bottom: 1rem;">
              <div style="background: var(--bg-tertiary); border-radius: 12px; padding: 2rem; text-align: center; color: var(--text-muted);">
                <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">📝</div>
                <p style="margin: 0; font-size: 0.875rem;">Text-only post</p>
                <p style="margin: 0; font-size: 0.75rem; opacity: 0.7;">Images disabled for faster generation</p>
              </div>
            </div>`}

        <div style="display: flex; flex-wrap: wrap; gap: 0.5rem;">
          ${mockHashtags.map((tag) => `<span class="badge bg-primary">${tag}</span>`).join('')}
        </div>

        <div style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid var(--border-color); display: flex; justify-content: space-between; align-items: center;">
          <div style="display: flex; flex-wrap: wrap; gap: 1rem; font-size: 0.875rem; color: var(--text-muted);">
            <span>👍 42</span>
            <span>💬 8 comments</span>
            <span>🔄 3 reposts</span>
          </div>
          <div style="font-size: 0.75rem; color: var(--text-muted);">
            ${includeImage ? 'Live Preview' : 'Text Preview'}
          </div>
        </div>
      </div>
    `;
  }

  generateMockContent(topic, postType, preferences) {
    const templates = {
      ai_news: [
        `Exciting developments in ${topic}! The latest breakthroughs are pushing boundaries and opening new possibilities. What are your thoughts on this emerging trend? 🤔`,
        `Just read about the latest in ${topic}. The innovation happening here is incredible. Here's what caught my attention…`,
        `The ${topic} landscape is evolving rapidly. Here are the key insights from recent developments that every tech professional should know.`,
      ],
      personal_milestone: [
        `Today marks an important milestone in my journey with ${topic}. Grateful for the opportunities and excited for what's next! 🚀`,
        `Reflecting on my experience with ${topic}. The lessons learned and growth achieved have been invaluable. Here's what I've discovered…`,
        `Celebrating progress in ${topic}! Sometimes the journey teaches us more than the destination. Here's my latest chapter.`,
      ],
    };

    let content = templates[postType] || templates.ai_news;
    let selectedContent = content[Math.floor(Math.random() * content.length)];

    if (preferences) {
      selectedContent += `\n\n(Preference: ${preferences})`;
    }

    return selectedContent;
  }

  generateMockHashtags(topic) {
    const base = ['#Tech', '#Innovation', '#FutureOfWork'];
    const words = topic.toLowerCase().split(' ').filter((w) => w.length > 3);
    const topicTags = words.map((w) => `#${w.charAt(0).toUpperCase() + w.slice(1)}`);
    return [...base, ...topicTags.slice(0, 3)];
  }
}

// Snackbar Notifications
class Snackbar {
  constructor() {
    this.container = null;
    this.init();
  }

  init() {
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
      ${
        actions.length > 0
          ? `<div class="snackbar-actions">
              ${actions
                .map(
                  (action) =>
                    `<button class="btn btn-sm btn-primary" onclick="${action.callback}">${action.label}</button>`
                )
                .join('')}
            </div>`
          : ''
      }
    `;
    this.container.appendChild(snackbar);
    setTimeout(() => {
      snackbar.classList.add('hide');
      setTimeout(() => {
        snackbar.remove();
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
    this.form?.addEventListener('submit', (e) => this.handleSubmit(e));
  }

    async handleSubmit(e) {
        e.preventDefault();
        const formData = new FormData(this.form);
        const preferences = formData.get('preferences');
        const includeImage = formData.get('include_image') === 'on'; // Correctly get checkbox state

        const postData = {
            topic: formData.get('topic'),
            post_type: formData.get('post_type'),
            user_preferences: preferences ? { general: preferences } : {},
            include_image: includeImage,
        };

        this.showLoading(true);
        this.hideError();

        // Show search status if web search is likely to be used
        const preview = new LivePreview('previewContent');
        preview.showSearchStatus(true);

        try {
            const response = await fetch('/generate-post', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(postData),
            });
            const result = await response.json();
            if (!response.ok) {
                throw new Error(result.detail || 'Generation failed');
            }
            this.currentSessionId = result.session_id;
            this.showPreview(result);
        } catch (err) {
            this.showError(err.message);
        } finally {
            this.showLoading(false);
            preview.showSearchStatus(false);
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
            ${data.hashtags.map((tag) => `<span class="badge bg-primary me-1">${tag}</span>`).join('')}
          </p>

          ${
            data.image_path
              ? `<h6 class="card-subtitle mb-2 text-muted mt-3">Generated Image:</h6>
                 <img src="/images/${data.image_path.split('/').pop()}" class="img-fluid rounded" alt="Generated image">`
              : `<h6 class="card-subtitle mb-2 text-muted mt-3">Image Prompt:</h6>
                 <p class="card-text text-muted">${data.image_prompt}</p>
                 <p class="text-warning"><small>⚠️ Image generation failed, but will be retried if you approve.</small></p>`
          }
        </div>
      </div>
    `;
    document.getElementById('postPreview').innerHTML = previewHtml;
    new bootstrap.Modal(document.getElementById('previewModal')).show();
  }

  showLoading(show) {
    if (this.loadingContainer) this.loadingContainer.style.display = show ? 'block' : 'none';
    const submitBtn = this.form?.querySelector('button[type="submit"]');
    if (submitBtn) submitBtn.disabled = show;
  }

  showError(msg) {
    if (this.errorAlert) {
      this.errorAlert.textContent = msg;
      this.errorAlert.style.display = 'block';
    }
  }

  hideError() {
    if (this.errorAlert) {
      this.errorAlert.style.display = 'none';
    }
  }
}

// Initialize on DOMContentLoaded
document.addEventListener('DOMContentLoaded', () => {
  new ThemeManager();
  new CharacterCounter('topic', 'charCount', 'progressCircle');
  new SegmentedControl('postTypeControl', 'post_type');
  new ImageToggle('includeImageToggle');
  new LivePreview('previewContent');
  new PostForm();

});
