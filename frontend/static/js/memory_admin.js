document.addEventListener('DOMContentLoaded', async () => {
    const memoryDataContainer = document.getElementById('memoryData');
    const loadingIndicator = document.getElementById('loadingIndicator');

    // Check if API is available
    if (!window.api || !window.api.get) {
        loadingIndicator.innerHTML = '<p class="error">API not available. Please refresh the page.</p>';
        return;
    }

    // Authentication Check
    try {
        const userData = await window.api.getCurrentUser();
        const user = userData.user;
        if (!user || user.role !== 'admin') {
            window.location.href = '/login';
            return;
        }

        document.getElementById('userName').textContent = user.username;
        document.getElementById('userRole').textContent = user.role;
    } catch (error) {
        console.error('Failed to get current user:', error);
        loadingIndicator.innerHTML = `<p class="error">Authentication failed. Redirecting to login...</p>`;
        setTimeout(() => window.location.href = '/login', 1000);
        return;
    }

    try {
        const memories = await window.api.get('/api/memory/all');

        if (!memories || memories.length === 0) {
            memoryDataContainer.innerHTML = '<p>No memory records found.</p>';
        } else {
            const memoriesByUser = memories.reduce((acc, memory) => {
                const userId = memory.user_id || 'unknown_user';
                if (!acc[userId]) {
                    acc[userId] = [];
                }
                acc[userId].push(memory);
                return acc;
            }, {});

            let html = '';
            for (const userId in memoriesByUser) {
                html += `
                    <div class="user-memory-group">
                        <h3>Patient (User ID: ${userId})</h3>
                        <div class="memory-records-grid">
                `;
                memoriesByUser[userId].forEach(memory => {
                    html += `
                        <div class="memory-card">
                            <p class="memory-content">${escapeHTML(memory.content)}</p>
                            ${memory.feedback ? `<p class="memory-feedback ${memory.feedback.toLowerCase()}">${escapeHTML(memory.feedback)}</p>` : ''}
                            <p class="memory-timestamp">${new Date(memory.timestamp).toLocaleString()}</p>
                        </div>
                    `;
                });
                html += `
                        </div>
                    </div>
                `;
            }
            memoryDataContainer.innerHTML = html;
        }

        loadingIndicator.style.display = 'none';
        memoryDataContainer.style.display = 'block';

    } catch (error) {
        console.error('Error fetching memory data:', error);
        console.error('Error details:', error.message);
        const errorMsg = error.message || 'Unknown error';
        loadingIndicator.innerHTML = `<p class="error">Failed to load memory records.</p><p style="font-size: 12px; color: #666; margin-top: 10px;">Error: ${escapeHTML(errorMsg)}</p>`;
        loadingIndicator.style.display = 'block';
    }
});

function escapeHTML(str) {
    return str.replace(/[&<>"']/g, function(match) {
        return {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#39;'
        }[match];
    });
}
