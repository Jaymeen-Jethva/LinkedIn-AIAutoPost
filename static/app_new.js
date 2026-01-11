// ============================================
// LinkedIn AI AutoPost - New Frontend Logic
// ============================================

// Validation constants
const MIN_TOPIC_LENGTH = 10;
const MAX_TOPIC_LENGTH = 500;
const DANGEROUS_CHARS_PATTERN = /[<>{}|\\^`]/;

// ================== SIDEBAR MANAGER ==================
class SidebarManager {
  constructor() {
    this.sidebar = document.getElementById('sidebar');
    this.toggle = document.getElementById('sidebarToggle');
    this.isExpanded = localStorage.getItem('sidebarExpanded') === 'true';
    this.init();
  }

  init() {
    if (this.isExpanded) {
      this.sidebar.classList.add('expanded');
    }
    
    this.toggle?.addEventListener('click', () => this.toggleSidebar());
    
    // Navigation items (currently frontend-only)
    document.querySelectorAll('.nav-item').forEach(item => {
      item.addEventListener('click', (e) => this.handleNavigation(e));
    });
  }

  toggleSidebar() {
    this.isExpanded = !this.isExpanded;
    this.sidebar.classList.toggle('expanded');
    localStorage.setItem('sidebarExpanded', this.isExpanded);
  }

  handleNavigation(e) {
    const page = e.currentTarget.dataset.page;
    
    // Remove active class from all items
    document.querySelectorAll('.nav-item').forEach(item => {
      item.classList.remove('active');
    });
    
    // Add active class to clicked item
    e.currentTarget.classList.add('active');
    
    // Handle page switching (currently only 'create' is functional)
    if (page !== 'create') {
      e.preventDefault();
      console.log(`Navigation to ${page} - Backend endpoint required`);
      // TODO: Implement routing when backend endpoints are ready
    }
  }
}

// ================== TONE PILL SELECTOR ==================
class TonePillSelector {
  constructor() {
    this.pills = document.querySelectorAll('.tone-pill');
    this.hiddenInput = document.getElementById('post_type');
    this.init();
  }

  init() {
    this.pills.forEach(pill => {
      pill.addEventListener('click', () => this.selectPill(pill));
    });
  }

  selectPill(selectedPill) {
    // Remove active class from all pills
    this.pills.forEach(pill => pill.classList.remove('active'));
    
    // Add active class to selected pill
    selectedPill.classList.add('active');
    
    // Update hidden input
    const tone = selectedPill.dataset.tone;
    if (this.hiddenInput) {
      this.hiddenInput.value = tone;
    }
  }
}

// ================== CHARACTER COUNTER ==================
class CharacterCounter {
  constructor() {
    this.textarea = document.getElementById('topic');
    this.counter = document.getElementById('charCount');
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
    
    // Visual feedback based on length
    if (length > this.maxLength * 0.9) {
      this.counter.style.color = 'var(--danger)';
    } else if (length > this.maxLength * 0.7) {
      this.counter.style.color = 'var(--warning)';
    } else {
      this.counter.style.color = 'var(--text-dim)';
    }
  }
}

// ================== LIVE PREVIEW ==================
class LivePreview {
  constructor() {
    this.previewText = document.getElementById('previewText');
    this.previewHashtags = document.getElementById('previewHashtags');
    this.previewImage = document.getElementById('previewImage');
    this.init();
  }

  init() {
    // Listen for form input changes
    const topic = document.getElementById('topic');
    const preferences = document.getElementById('preferences');
    const imageToggle = document.getElementById('includeImageToggle');

    topic?.addEventListener('input', () => this.updatePreview());
    preferences?.addEventListener('input', () => this.updatePreview());
    imageToggle?.addEventListener('change', () => this.updatePreview());
    
    // Listen for tone changes
    document.querySelectorAll('.tone-pill').forEach(pill => {
      pill.addEventListener('click', () => setTimeout(() => this.updatePreview(), 100));
    });
  }

  updatePreview() {
    const topic = document.getElementById('topic')?.value || '';
    const tone = document.getElementById('post_type')?.value || 'professional';
    const preferences = document.getElementById('preferences')?.value || '';
    const includeImage = document.getElementById('includeImageToggle')?.checked;

    if (topic.length > 10) {
      const mockContent = this.generateMockContent(topic, tone, preferences);
      const mockHashtags = this.generateMockHashtags(topic);
      
      this.previewText.textContent = mockContent;
      
      // Update hashtags
      this.previewHashtags.innerHTML = mockHashtags
        .map(tag => `<span class="linkedin-hashtag">${tag}</span>`)
        .join(' ');
      
      // Show/hide image placeholder
      if (includeImage) {
        this.previewImage.style.display = 'flex';
      } else {
        this.previewImage.style.display = 'none';
      }
    } else {
      this.previewText.textContent = 'Your generated LinkedIn post will appear here. Fill out the form and click "Generate Post" to see your AI-powered content come to life! ✨';
      this.previewHashtags.innerHTML = '';
      this.previewImage.style.display = 'none';
    }
  }

  generateMockContent(topic, tone, preferences) {
    const templates = {
      professional: [
        `Exciting developments in ${topic}! The latest insights are reshaping how we approach this field. Here are the key takeaways every professional should know. 🎯`,
        `I've been exploring ${topic} recently, and the innovation happening here is remarkable. Here's what stood out to me...`,
      ],
      viral: [
        `🚀 ${topic} is about to EXPLODE! Here's the insider perspective everyone needs to hear...`,
        `Stop scrolling! This is the ${topic} breakthrough you've been waiting for. Thread 🧵👇`,
      ],
      story: [
        `Let me share a story about ${topic}. It started when I first discovered this fascinating field...`,
        `My journey with ${topic} taught me lessons I never expected. Here's what happened...`,
      ],
      insightful: [
        `After analyzing ${topic} for months, here are the patterns nobody's talking about 💡`,
        `The deeper you look into ${topic}, the more interesting it becomes. Let me explain why...`,
      ],
      direct: [
        `${topic}: Here's what matters. No fluff, just facts. 🎯`,
        `Let's cut to the chase about ${topic}. Here are the 3 things you need to know.`,
      ],
    };

    const toneTemplates = templates[tone] || templates.professional;
    let content = toneTemplates[Math.floor(Math.random() * toneTemplates.length)];

    if (preferences) {
      content += `\n\n(Note: ${preferences})`;
    }

    return content;
  }

  generateMockHashtags(topic) {
    const base = ['#LinkedIn', '#Professional', '#Growth'];
    const words = topic.toLowerCase().split(' ').filter(w => w.length > 3);
    const topicTags = words.slice(0, 3).map(w => `#${w.charAt(0).toUpperCase() + w.slice(1)}`);
    return [...base, ...topicTags].slice(0, 6);
  }
}

// ================== SNACKBAR NOTIFICATIONS ==================
class Snackbar {
  constructor() {
    this.container = null;
    this.init();
  }

  init() {
    if (!document.querySelector('.snackbar-container')) {
      this.container = document.createElement('div');
      this.container.className = 'snackbar-container';
      this.container.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        z-index: 10000;
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
      `;
      document.body.appendChild(this.container);
    } else {
      this.container = document.querySelector('.snackbar-container');
    }
  }

  show(message, duration = 4000) {
    const snackbar = document.createElement('div');
    snackbar.style.cssText = `
      background: var(--bg-secondary);
      border: 1px solid var(--glass-border);
      border-radius: 12px;
      padding: 1rem 1.5rem;
      box-shadow: var(--shadow-lg);
      color: var(--text-primary);
      font-size: 0.9375rem;
      animation: slideIn 0.3s ease;
    `;
    snackbar.textContent = message;
    
    this.container.appendChild(snackbar);
    
    setTimeout(() => {
      snackbar.style.animation = 'slideOut 0.3s ease forwards';
      setTimeout(() => snackbar.remove(), 300);
    }, duration);
  }
}

// ================== POST FORM HANDLER ==================
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
    this.setupActionListeners();
  }

  setupActionListeners() {
    console.log("Setting up action listeners using event delegation");

    // Use event delegation for modal buttons
    document.addEventListener('click', (e) => {
      // Approve Button
      if (e.target.closest('#approveBtn')) {
        console.log("Approve button clicked");
        e.preventDefault();
        this.handleApprove();
        return;
      }

      // Revision Button
      if (e.target.closest('#reviseBtn')) {
        console.log("Revise button clicked");
        e.preventDefault();
        new bootstrap.Modal(document.getElementById('revisionModal')).show();
        return;
      }

      // Submit Revision Button
      if (e.target.closest('#submitRevision')) {
        console.log("Submit revision clicked");
        e.preventDefault();
        this.handleSubmitRevision();
        return;
      }
    });
  }

  async handleApprove() {
    console.log("handleApprove called. Session ID:", this.currentSessionId);

    if (!this.currentSessionId) {
      alert("Error: No active session found. Please try generating the post again.");
      return;
    }

    const btn = document.getElementById('approveBtn');
    const originalText = btn.innerHTML;
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Posting...';

    try {
      const response = await fetch('/approve-post', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: this.currentSessionId,
          approved: true,
        }),
      });

      const result = await response.json();

      if (result.success) {
        bootstrap.Modal.getInstance(document.getElementById('previewModal')).hide();
        this.snackbar.show('🎉 Post published successfully to LinkedIn!', 5000);
      } else {
        alert('Error: ' + (result.message || 'Posting failed'));
      }
    } catch (err) {
      alert('Error: ' + err.message);
    } finally {
      btn.disabled = false;
      btn.innerHTML = originalText;
    }
  }

  async handleSubmitRevision() {
    const feedbackInput = document.getElementById('feedbackText');
    const feedback = feedbackInput.value.trim();

    if (!this.currentSessionId || !feedback) {
      alert('Please provide feedback');
      return;
    }

    const btn = document.getElementById('submitRevision');
    const originalText = btn.innerHTML;
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Revising...';

    try {
      const response = await fetch('/approve-post', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: this.currentSessionId,
          approved: false,
          feedback: feedback,
        }),
      });

      const result = await response.json();

      if (result.revised) {
        this.showPreview(result);
        bootstrap.Modal.getInstance(document.getElementById('revisionModal')).hide();
        feedbackInput.value = '';
        this.snackbar.show('Content revised! Check the new draft.');
      } else {
        alert('Revision failed');
      }
    } catch (err) {
      alert('Error: ' + err.message);
    } finally {
      btn.disabled = false;
      btn.innerHTML = originalText;
    }
  }

  async handleSubmit(e) {
    e.preventDefault();
    const formData = new FormData(this.form);
    const topic = formData.get('topic')?.trim() || '';
    const preferences = formData.get('preferences');
    const includeImage = formData.get('include_image') === 'on';

    // Validation
    const validationError = this.validateInput(topic);
    if (validationError) {
      this.showError(validationError);
      return;
    }

    const postData = {
      topic: topic,
      post_type: formData.get('post_type'),
      user_preferences: preferences ? { general: preferences } : {},
      include_image: includeImage,
    };

    this.showLoading(true);
    this.hideError();

    try {
      const response = await fetch('/generate-post', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
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
    }
  }

  showPreview(data) {
    const previewHtml = `
      <div class="glass-card" style="padding: 1.5rem;">
        <h6 style="color: var(--text-muted); font-size: 0.875rem; margin-bottom: 0.75rem;">Generated Content:</h6>
        <p style="color: var(--text-secondary); line-height: 1.6; white-space: pre-wrap;">${data.content.replace(/\n/g, '<br>')}</p>

        <h6 style="color: var(--text-muted); font-size: 0.875rem; margin-top: 1.5rem; margin-bottom: 0.75rem;">Hashtags:</h6>
        <p>
          ${data.hashtags.map(tag => `<span class="linkedin-hashtag">${tag}</span>`).join(' ')}
        </p>

        ${data.image_path
          ? `<h6 style="color: var(--text-muted); font-size: 0.875rem; margin-top: 1.5rem; margin-bottom: 0.75rem;">Generated Image:</h6>
             <img src="/images/${data.image_path.split('/').pop()}" style="width: 100%; border-radius: 12px;" alt="Generated image">`
          : `<h6 style="color: var(--text-muted); font-size: 0.875rem; margin-top: 1.5rem; margin-bottom: 0.75rem;">Image Prompt:</h6>
             <p style="color: var(--text-muted); font-size: 0.875rem;">${data.image_prompt}</p>
             <p style="color: var(--warning); font-size: 0.875rem;">⚠️ Image generation failed, but will be retried if you approve.</p>`
        }
      </div>
    `;
    
    document.getElementById('postPreview').innerHTML = previewHtml;
    new bootstrap.Modal(document.getElementById('previewModal')).show();
  }

  showLoading(show) {
    if (this.loadingContainer) {
      if (show) {
        this.loadingContainer.classList.add('active');
      } else {
        this.loadingContainer.classList.remove('active');
      }
    }
    
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

  validateInput(topic) {
    if (!topic) {
      return 'Please enter a topic for your post';
    }
    if (topic.length < MIN_TOPIC_LENGTH) {
      return `Topic must be at least ${MIN_TOPIC_LENGTH} characters long (currently ${topic.length})`;
    }
    if (topic.length > MAX_TOPIC_LENGTH) {
      return `Topic must not exceed ${MAX_TOPIC_LENGTH} characters (currently ${topic.length})`;
    }
    if (DANGEROUS_CHARS_PATTERN.test(topic)) {
      return 'Topic contains invalid characters. Please remove: < > { } | \\ ^ `';
    }
    return null;
  }
}

// ================== LINKEDIN CONNECTION MANAGER ==================
class LinkedInConnection {
  constructor() {
    this.connectBtn = document.getElementById('linkedinConnectBtn');
    this.disconnectBtn = document.getElementById('linkedinDisconnectBtn');
    this.connectedEl = document.getElementById('linkedinConnected');
    this.disconnectedEl = document.getElementById('linkedinDisconnected');
    this.snackbar = new Snackbar();
    this.init();
  }

  init() {
    this.checkStatus();
    this.handleOAuthRedirect();
    
    this.connectBtn?.addEventListener('click', () => this.connect());
    this.disconnectBtn?.addEventListener('click', () => this.disconnect());
  }

  handleOAuthRedirect() {
    const urlParams = new URLSearchParams(window.location.search);

    if (urlParams.has('linkedin_connected')) {
      this.snackbar.show('✅ Successfully connected to LinkedIn!', 5000);
      window.history.replaceState({}, document.title, window.location.pathname);
      this.checkStatus();
    }

    if (urlParams.has('linkedin_error')) {
      const error = urlParams.get('linkedin_error');
      this.snackbar.show(`❌ LinkedIn connection failed: ${error}`, 6000);
      window.history.replaceState({}, document.title, window.location.pathname);
    }
  }

  async checkStatus() {
    try {
      const response = await fetch('/linkedin/status');
      const data = await response.json();

      if (data.connected) {
        this.showConnected();
      } else {
        this.showDisconnected();
      }
    } catch (err) {
      console.error('Failed to check LinkedIn status:', err);
      this.showDisconnected();
    }
  }

  async connect() {
    try {
      this.connectBtn.disabled = true;
      const originalHTML = this.connectBtn.innerHTML;
      this.connectBtn.innerHTML = '<span style="font-size: 0.75rem;">...</span>';

      const response = await fetch('/linkedin/connect', { method: 'POST' });
      const data = await response.json();

      if (data.authorization_url) {
        window.location.href = data.authorization_url;
      } else {
        throw new Error(data.detail || 'Failed to get authorization URL');
      }
    } catch (err) {
      this.snackbar.show(`❌ ${err.message}`, 5000);
      this.connectBtn.disabled = false;
      this.connectBtn.innerHTML = 'Connect';
    }
  }

  async disconnect() {
    if (!confirm('Are you sure you want to disconnect LinkedIn?')) {
      return;
    }

    try {
      this.disconnectBtn.disabled = true;

      const response = await fetch('/linkedin/disconnect', { method: 'POST' });
      const data = await response.json();

      if (data.success) {
        this.snackbar.show('✅ Disconnected from LinkedIn', 4000);
        this.showDisconnected();
      } else {
        throw new Error(data.detail || 'Disconnect failed');
      }
    } catch (err) {
      this.snackbar.show(`❌ ${err.message}`, 5000);
      this.disconnectBtn.disabled = false;
    }
  }

  showConnected() {
    if (this.connectedEl) this.connectedEl.style.display = 'flex';
    if (this.disconnectedEl) this.disconnectedEl.style.display = 'none';
  }

  showDisconnected() {
    if (this.connectedEl) this.connectedEl.style.display = 'none';
    if (this.disconnectedEl) this.disconnectedEl.style.display = 'flex';
  }
}

// ================== INITIALIZE ON DOM LOAD ==================
document.addEventListener('DOMContentLoaded', () => {
  console.log('LinkedIn AI AutoPost - Initializing...');
  
  // Initialize all components
  new SidebarManager();
  new TonePillSelector();
  new CharacterCounter();
  new LivePreview();
  new PostForm();
  new LinkedInConnection();
  
  console.log('All components initialized successfully!');
});

// Add CSS animations for snackbar
const style = document.createElement('style');
style.textContent = `
  @keyframes slideIn {
    from {
      transform: translateX(100%);
      opacity: 0;
    }
    to {
      transform: translateX(0);
      opacity: 1;
    }
  }
  
  @keyframes slideOut {
    from {
      transform: translateX(0);
      opacity: 1;
    }
    to {
      transform: translateX(100%);
      opacity: 0;
    }
  }
`;
document.head.appendChild(style);
