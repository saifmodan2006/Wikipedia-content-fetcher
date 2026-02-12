// Utility Functions
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 20px;
        background-color: ${type === 'success' ? '#4caf50' : type === 'error' ? '#f44336' : '#2196f3'};
        color: white;
        border-radius: 5px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.2);
        z-index: 1000;
        animation: slideIn 0.3s ease;
    `;

    document.body.appendChild(notification);

    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Add animation styles
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(400px);
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
            transform: translateX(400px);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

// API Request Helper
async function apiRequest(url, options = {}) {
    try {
        const response = await fetch(url, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'API request failed');
        }

        return data;
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

// Debounce Function
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Export functions for use in templates
window.downloadContent = function(contentId, format) {
    const form = document.createElement('form');
    form.method = 'POST';
    form.action = `/api/download/${contentId}?format=${format}`;
    document.body.appendChild(form);
    form.submit();
    document.body.removeChild(form);
    showNotification(`Downloading as ${format.toUpperCase()}...`, 'info');
};

window.loadTopicContent = function(topicId) {
    const previewSection = document.getElementById('previewSection');
    const previewContainer = document.getElementById('previewContainer');

    if (!previewSection || !previewContainer) return;

    previewSection.style.display = 'block';
    previewContainer.innerHTML = '<div class="loading">Loading content...</div>';

    fetch(`/api/topics/${topicId}/content`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                displayContentPreview(data.topic, data.content, previewContainer);
                previewSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
            } else {
                previewContainer.innerHTML = '<div class="error">Failed to load content</div>';
                showNotification('Failed to load content', 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            previewContainer.innerHTML = '<div class="error">Error loading content</div>';
            showNotification('Error loading content', 'error');
        });
};

window.displayContentPreview = function(topic, contentList, container) {
    if (contentList.length === 0) {
        container.innerHTML = '<div class="message">No content available for this topic</div>';
        return;
    }

    container.innerHTML = contentList.map(content => `
        <div class="content-item">
            <div class="content-header">
                <h3>${escapeHtml(content.title)}</h3>
            </div>
            <div class="content-body">
                <h4>Explanation:</h4>
                <div class="explanation">${escapeHtml(content.explanation).replace(/\n/g, '<br>')}</div>

                ${content.code_examples ? `
                    <h4>Code Examples:</h4>
                    <pre class="code-examples">${escapeHtml(content.code_examples)}</pre>
                ` : ''}
            </div>
            <div class="content-footer">
                <div class="download-options">
                    <p>Download as:</p>
                    <button class="btn btn-small" onclick="downloadContent(${content.id}, 'pdf')">📄 PDF</button>
                    <button class="btn btn-small" onclick="downloadContent(${content.id}, 'text')">📝 Text</button>
                    <button class="btn btn-small" onclick="downloadContent(${content.id}, 'markdown')">📋 Markdown</button>
                </div>
            </div>
        </div>
    `).join('');
};

// Export other functions
window.performSearch = function(query) {
    const resultsContainer = document.getElementById('resultsContainer');
    if (!resultsContainer) return;

    resultsContainer.innerHTML = '<div class="loading">Searching...</div>';

    fetch(`/api/topics/search?q=${encodeURIComponent(query)}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                displaySearchResults(data.data, resultsContainer);
            } else {
                resultsContainer.innerHTML = '<div class="error">Search failed</div>';
                showNotification('Search failed', 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            resultsContainer.innerHTML = '<div class="error">Error performing search</div>';
            showNotification('Error performing search', 'error');
        });
};

window.displaySearchResults = function(topics, container) {
    if (topics.length === 0) {
        container.innerHTML = '<div class="message">No topics found matching your search</div>';
        const previewSection = document.getElementById('previewSection');
        if (previewSection) previewSection.style.display = 'none';
        return;
    }

    container.innerHTML = topics.map(topic => `
        <div class="result-card">
            <h3>${escapeHtml(topic.name)}</h3>
            <p>${escapeHtml(topic.description || 'No description available')}</p>
            <button class="btn btn-secondary" onclick="loadTopicContent(${topic.id})">
                View Content
            </button>
        </div>
    `).join('');
};

window.displayTopics = function(topics, container) {
    if (topics.length === 0) {
        container.innerHTML = '<div class="message">No topics found</div>';
        return;
    }

    container.innerHTML = topics.map(topic => `
        <div class="topic-card">
            <h3>${escapeHtml(topic.name)}</h3>
            <p>${escapeHtml(topic.description || 'No description available')}</p>
            <a href="/search?topic=${encodeURIComponent(topic.name)}" class="btn btn-primary">
                View Content
            </a>
        </div>
    `).join('');
};

window.loadTopics = function() {
    const container = document.getElementById('topicsContainer');
    if (!container) return;

    container.innerHTML = '<div class="loading">Loading topics...</div>';

    fetch('/api/topics')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                displayTopics(data.data, container);
            } else {
                container.innerHTML = '<div class="error">Failed to load topics</div>';
                showNotification('Failed to load topics', 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            container.innerHTML = '<div class="error">Error loading topics</div>';
            showNotification('Error loading topics', 'error');
        });
};

window.setupQuickSearch = function() {
    const searchInput = document.getElementById('quickSearch');
    if (!searchInput) return;

    let debounceTimer;

    searchInput.addEventListener('input', function(e) {
        clearTimeout(debounceTimer);
        const query = e.target.value.trim();

        if (query.length < 2) {
            loadTopics();
            return;
        }

        debounceTimer = setTimeout(() => {
            fetch(`/api/topics/search?q=${encodeURIComponent(query)}`)
                .then(response => response.json())
                .then(data => {
                    const container = document.getElementById('topicsContainer');
                    if (container && data.success) {
                        displayTopics(data.data, container);
                    }
                })
                .catch(error => console.error('Search error:', error));
        }, 300);
    });
};

window.setupSearch = function() {
    const searchInput = document.getElementById('searchInput');
    const searchBtn = document.getElementById('searchBtn');

    if (!searchInput || !searchBtn) return;

    searchBtn.addEventListener('click', () => {
        const query = searchInput.value.trim();
        if (query) window.performSearch(query);
    });

    searchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            const query = searchInput.value.trim();
            if (query) window.performSearch(query);
        }
    });
};
