const chatViewport = document.getElementById('chatViewport');
const emptyState = document.getElementById('emptyState');
const chatFeed = document.getElementById('chatFeed');
const inputForm = document.getElementById('inputForm');
const queryInput = document.getElementById('queryInput');
const sendBtn = document.getElementById('sendBtn');
const sidebar = document.getElementById('sidebar');
const sidebarBackdrop = document.getElementById('sidebarBackdrop');

let isSidebarOpen = false;
let typingIndicator = null;

// Toggle mobile sidebar drawer
function toggleSidebar(open) {
    isSidebarOpen = open;
    if (open) {
        sidebar.classList.add('translate-x-0');
        sidebarBackdrop.classList.remove('hidden');
    } else {
        sidebar.classList.remove('translate-x-0');
        sidebarBackdrop.classList.add('hidden');
    }
}

// Reset chat viewport to empty state
function resetChat() {
    chatFeed.innerHTML = '';
    chatFeed.classList.add('hidden');
    emptyState.classList.remove('hidden');
    queryInput.value = '';
    toggleSidebar(false);
}

// Automatically scroll viewport to bottom
function scrollToBottom() {
    chatViewport.scrollTo({
        top: chatViewport.scrollHeight,
        behavior: 'smooth'
    });
}

// Multi-stage delay helper
const delay = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

// Format Markdown Links [Label](URL) safely
function formatMarkdownLinks(text) {
    // Escape HTML to prevent XSS
    let safeText = text
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
        
    const linkRegex = /\[([^\]]+)\]\((https?:\/\/[^\s)]+)\)/g;
    return safeText.replace(linkRegex, '<a href="$2" target="_blank" rel="noopener noreferrer" class="source-card-right" style="text-decoration: underline;">$1</a>');
}

// Safe URL source label resolver
function getSourceLabel(link) {
    try {
        const parsed = new URL(link);
        if (parsed.hostname.includes("groww")) return "Official Groww AMC Factsheet";
        if (parsed.hostname.includes("sebi")) return "SEBI Investor Portal";
        if (parsed.hostname.includes("amfi")) return "AMFI Official Portal";
        return `${parsed.hostname} Document`;
    } catch {
        return "Official Fund Factsheet";
    }
}

// Render dynamic User Message Bubble
function appendUserMessage(text) {
    const wrapper = document.createElement('div');
    wrapper.className = 'chat-row-user';

    const bubble = document.createElement('div');
    bubble.className = 'user-bubble animate-slide-in-right';
    bubble.textContent = text;

    wrapper.appendChild(bubble);
    chatFeed.appendChild(wrapper);
    scrollToBottom();
}

// Render dynamic Assistant Card (Factual, Refusal, PII, System error)
function appendAssistantMessage(data) {
    const wrapper = document.createElement('div');
    wrapper.className = 'chat-row-assistant animate-fade-in';

    const status = data.status; // "success", "violated", "error"
    const type = data.type;     // "advisory", "pii", "system"
    const text = data.answer;
    const sourceUrl = data.source_url;
    const lastUpdated = data.last_updated;

    // 1. ADVISORY VIOLATION REFUSAL CARD (Amber Warning UI)
    if (status === 'violated' && type === 'advisory') {
        const amfiUrl = sourceUrl || "https://www.amfiindia.com/investor-corner/knowledge-center/tax-benefits.html";
        wrapper.innerHTML = `
            <div class="refusal-card">
                <div class="refusal-flex">
                    <svg width="20" height="20" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24" style="margin-top: 2px;">
                        <path d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path>
                    </svg>
                    <div>
                        <h4 class="refusal-title">Facts-Only Assistant</h4>
                        <p class="refusal-text">${text}</p>
                        <a href="${amfiUrl}" target="_blank" rel="noopener noreferrer" class="refusal-action-link">
                            <span>Learn More at AMFI</span>
                            <svg width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24">
                                <line x1="5" y1="12" x2="19" y2="12"></line>
                                <polyline points="12 5 19 12 12 19"></polyline>
                            </svg>
                        </a>
                    </div>
                </div>
            </div>
        `;
    }
    // 2. PRIVACY INTERCEPT CARD (Red Warning UI)
    else if (status === 'violated' && type === 'pii') {
        wrapper.innerHTML = `
            <div class="privacy-card">
                <div class="privacy-flex">
                    <svg width="20" height="20" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24" style="margin-top: 2px;">
                        <path d="M12 15v2m0-8V7m0 0v2m0-2a3 3 0 116 0v6a3 3 0 01-3 3z"></path>
                        <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
                    </svg>
                    <div>
                        <h4 class="privacy-title">Privacy Intercepted</h4>
                        <p class="privacy-text">${text}</p>
                    </div>
                </div>
            </div>
        `;
    }
    // 3. UNRELATED QUERY REFUSAL CARD (Info / Blue UI)
    else if (status === 'violated' && type === 'unrelated') {
        wrapper.innerHTML = `
            <div class="info-card animate-fade-in">
                <div class="info-flex">
                    <svg width="20" height="20" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24">
                        <circle cx="12" cy="12" r="10"></circle>
                        <line x1="12" y1="16" x2="12" y2="12"></line>
                        <line x1="12" y1="8" x2="12.01" y2="8"></line>
                    </svg>
                    <div>
                        <h4 class="info-title">Groww MF FAQ Assistant</h4>
                        <p class="info-text">${text}</p>
                    </div>
                </div>
            </div>
        `;
    }
    // 4. SYSTEM NOTIFICATION / ERRORS
    else if (status === 'error') {
        wrapper.innerHTML = `
            <div class="system-card">
                <div class="system-flex">
                    <svg width="20" height="20" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24" style="margin-top: 2px;">
                        <circle cx="12" cy="12" r="10"></circle>
                        <line x1="12" y1="16" x2="12" y2="12"></line>
                        <line x1="12" y1="8" x2="12.01" y2="8"></line>
                    </svg>
                    <div>
                        <h4 class="system-title">System Notification</h4>
                        <p class="system-text">${text}</p>
                    </div>
                </div>
            </div>
        `;
    }
    // 4. FACTUAL CITATION CARD (Groww Green Accent)
    else {
        const sourceHtml = sourceUrl ? `
            <a href="${sourceUrl}" target="_blank" rel="noopener noreferrer" class="source-card">
                <div class="source-card-left">
                    <svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24">
                        <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                    </svg>
                    <div>
                        <span class="source-card-tag">Verified Source</span>
                        <span class="source-card-title">${getSourceLabel(sourceUrl)}</span>
                    </div>
                </div>
                <div class="source-card-right">
                    <span>View Source</span>
                    <svg width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24">
                        <path d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"></path>
                    </svg>
                </div>
            </a>
        ` : '';

        const dateHtml = lastUpdated ? `
            <div class="answer-card-timestamp">
                <svg width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24">
                    <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
                    <line x1="16" y1="2" x2="16" y2="6"></line>
                    <line x1="8" y1="2" x2="8" y2="6"></line>
                    <line x1="3" y1="10" x2="21" y2="10"></line>
                </svg>
                <span>Last updated from sources: ${lastUpdated}</span>
            </div>
        ` : '';

        const footerHtml = (sourceHtml || dateHtml) ? `
            <div class="answer-card-footer">
                ${dateHtml}
                ${sourceHtml}
            </div>
        ` : '';

        wrapper.innerHTML = `
            <div class="answer-card">
                <div class="answer-card-header">
                    <svg width="20" height="20" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24">
                        <path d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"></path>
                    </svg>
                    <span>Verified Information</span>
                </div>
                <p class="answer-card-body">
                    ${formatMarkdownLinks(text)}
                </p>
                ${footerHtml}
            </div>
        `;
    }

    chatFeed.appendChild(wrapper);
    scrollToBottom();
}

// Show multi-stage animated skeleton loader
async function showSkeletonLoader() {
    if (typingIndicator) return;

    typingIndicator = document.createElement('div');
    typingIndicator.className = 'chat-row-assistant animate-pulse shrink-0';
    
    typingIndicator.innerHTML = `
        <div class="answer-card">
            <div class="answer-card-header">
                <div style="width: 20px; height: 20px; border-radius: 50%; background-color: var(--border-color);"></div>
                <div style="width: 120px; height: 14px; background-color: var(--border-color); border-radius: 4px; margin-left: 8px;"></div>
            </div>
            <div style="display: flex; flex-direction: column; gap: 8px; margin-top: 12px;">
                <div class="skeleton-shimmer" style="height: 16px; background-color: var(--border-light); border-radius: 4px; width: 100%;"></div>
                <div class="skeleton-shimmer" style="height: 16px; background-color: var(--border-light); border-radius: 4px; width: 90%;"></div>
                <div class="skeleton-shimmer" style="height: 16px; background-color: var(--border-light); border-radius: 4px; width: 60%;"></div>
            </div>
            <div style="display: flex; align-items: center; gap: 10px; margin-top: 20px; padding-top: 12px; border-top: 1px solid var(--border-light);">
                <div class="typing-loader">
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                </div>
                <span style="font-size: 11px; font-weight: 750; color: var(--groww-green);" id="loaderStage">Searching official sources...</span>
            </div>
        </div>
    `;

    chatFeed.appendChild(typingIndicator);
    scrollToBottom();

    // Transition stages
    await delay(600);
    const stage1 = document.getElementById('loaderStage');
    if (stage1) stage1.textContent = 'Verifying information safety...';
    
    await delay(600);
    const stage2 = document.getElementById('loaderStage');
    if (stage2) stage2.textContent = 'Compiling response from official docs...';
    
    await delay(400);
}

// Remove animated loader
function removeSkeletonLoader() {
    if (typingIndicator) {
        typingIndicator.remove();
        typingIndicator = null;
    }
}

// Primary submit action
async function submitQuery(queryText) {
    const trimmed = queryText.trim();
    if (!trimmed) return;

    // Toggle layouts: hide starter grid, show scroll viewport
    emptyState.classList.add('hidden');
    chatFeed.classList.remove('hidden');
    toggleSidebar(false);

    // 1. Output User Bubble
    appendUserMessage(trimmed);
    queryInput.value = '';
    queryInput.style.height = 'auto';

    // 2. Start loaders
    await showSkeletonLoader();

    // 3. Dispatches payload
    try {
        const response = await fetch('/api/query', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ query: trimmed })
        });

        removeSkeletonLoader();

        if (response.ok) {
            const data = await response.json();
            appendAssistantMessage({
                status: data.status,
                type: data.type,
                answer: data.answer || "An unexpected error occurred.",
                source_url: data.source_url,
                last_updated: data.last_updated
            });
        } else {
            appendAssistantMessage({
                status: 'error',
                answer: 'The assistant is temporarily unavailable. Please try again shortly.'
            });
        }
    } catch (error) {
        removeSkeletonLoader();
        console.error('Fetch error:', error);
        appendAssistantMessage({
            status: 'error',
            answer: 'Connection failed. Please ensure the backend FastAPI service is running locally.'
        });
    }
}

// Fetch supported AMCs dynamically on startup
async function loadMetadata() {
    const listContainer = document.getElementById('supportedAmcsList');
    if (!listContainer) return;

    try {
        const response = await fetch('/api/metadata');
        if (response.ok) {
            const data = await response.json();
            const amcs = data.amcs || [];
            if (amcs.length > 0) {
                renderAmcList(amcs);
                return;
            }
        }
    } catch (e) {
        console.error("Failed to load metadata from API:", e);
    }

    // Fallback list of AMCs if API fails or returns empty
    const fallbackAmcs = [
        "SBI Mutual Fund",
        "HDFC Mutual Fund",
        "ICICI Prudential Mutual Fund",
        "Kotak Mahindra Mutual Fund",
        "Axis Mutual Fund",
        "Mirae Asset Mutual Fund",
        "Nippon India Mutual Fund",
        "Tata Mutual Fund",
        "UTI Mutual Fund",
        "Groww Mutual Fund"
    ];
    renderAmcList(fallbackAmcs);
}

// Render lists of supported AMCs in the sidebar
function renderAmcList(amcs) {
    const listContainer = document.getElementById('supportedAmcsList');
    if (!listContainer) return;
    
    listContainer.innerHTML = '';
    amcs.forEach(amc => {
        const btn = document.createElement('button');
        btn.className = 'sidebar-nav-item';
        btn.style.fontSize = '0.8rem';
        btn.style.padding = '6px 12px';
        btn.onclick = () => {
            submitQuery(`What schemes are in ${amc}?`);
        };
        
        btn.innerHTML = `
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path>
            </svg>
            <span class="truncate">${amc}</span>
        `;
        listContainer.appendChild(btn);
    });
}

// Textarea auto-sizing key events
queryInput.addEventListener('input', function() {
    this.style.height = 'auto';
    this.style.height = Math.min(this.scrollHeight, 120) + 'px';
});

// Keypress triggers (Enter submits)
function handleTextareaKeydown(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        submitQuery(queryInput.value);
    }
}

// Form wrapper event
function handleFormSubmit(event) {
    event.preventDefault();
    submitQuery(queryInput.value);
}

// Theme Toggle Logic
function initTheme() {
    const savedTheme = localStorage.getItem('theme') || 'dark';
    setTheme(savedTheme);
}

function setTheme(theme) {
    const sunIcon = document.getElementById('sunIcon');
    const moonIcon = document.getElementById('moonIcon');
    
    if (theme === 'light') {
        document.documentElement.setAttribute('data-theme', 'light');
        localStorage.setItem('theme', 'light');
        if (sunIcon && moonIcon) {
            sunIcon.classList.add('hidden');
            moonIcon.classList.remove('hidden');
        }
    } else {
        document.documentElement.removeAttribute('data-theme');
        localStorage.setItem('theme', 'dark');
        if (sunIcon && moonIcon) {
            sunIcon.classList.remove('hidden');
            moonIcon.classList.add('hidden');
        }
    }
}

function toggleTheme() {
    const currentTheme = localStorage.getItem('theme') || 'dark';
    const nextTheme = currentTheme === 'dark' ? 'light' : 'dark';
    setTheme(nextTheme);
}

// Run metadata and theme init on page load
window.addEventListener('DOMContentLoaded', () => {
    initTheme();
    loadMetadata();
});
