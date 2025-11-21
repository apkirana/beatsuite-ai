/**
 * API Utilities
 * Helper functions for making authenticated API calls
 */

// Note: API_BASE is defined globally in auth.js as window.API_BASE

/**
 * Make authenticated API request
 */
async function apiRequest(endpoint, options = {}) {
    const API_BASE = window.API_BASE || '/api';
    const config = {
        ...options,
        credentials: 'include',  // Include cookies
        headers: {
            'Content-Type': 'application/json',
            ...options.headers
        }
    };
    
    try {
        const response = await fetch(`${API_BASE}${endpoint}`, config);
        
        // Handle 401 Unauthorized
        if (response.status === 401) {
            console.warn('Unauthorized - redirecting to login');
            window.location.href = '/login';
            return null;
        }
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || `HTTP ${response.status}`);
        }
        
        return data;
    } catch (error) {
        console.error('API request error:', error);
        throw error;
    }
}

/**
 * Get all rooms
 */
async function getRooms() {
    return apiRequest('/rooms');
}

/**
 * Get specific room data
 */
async function getRoomData(roomId) {
    return apiRequest(`/rooms/${roomId}`);
}

/**
 * Override AI for a room
 */
async function overrideAI(roomId, settings) {
    return apiRequest(`/rooms/${roomId}/override`, {
        method: 'POST',
        body: JSON.stringify(settings)
    });
}

/**
 * Resume AI for a room
 */
async function resumeAI(roomId) {
    return apiRequest(`/rooms/${roomId}/resume`, {
        method: 'POST'
    });
}

/**
 * Get current user info
 */
async function getCurrentUser() {
    return apiRequest('/auth/me');
}

/**
 * Generic GET request
 */
async function get(endpoint) {
    const response = await fetch(endpoint, {
        method: 'GET',
        credentials: 'include',
        headers: {
            'Content-Type': 'application/json'
        }
    });

    if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
    }

    return response.json();
}

/**
 * Generic POST request
 */
async function post(endpoint, data) {
    return fetch(endpoint, {
        method: 'POST',
        credentials: 'include',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    });
}

/**
 * Generic PUT request
 */
async function put(endpoint, data) {
    return fetch(endpoint, {
        method: 'PUT',
        credentials: 'include',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    });
}

/**
 * Generic DELETE request
 */
async function del(endpoint) {
    return fetch(endpoint, {
        method: 'DELETE',
        credentials: 'include',
        headers: {
            'Content-Type': 'application/json'
        }
    });
}

// Export functions
window.api = {
    getRooms,
    getRoomData,
    overrideAI,
    resumeAI,
    getCurrentUser,
    get
};

// Export CRUD utilities for admin panel
window.apiUtils = {
    get,
    post,
    put,
    delete: del
};
