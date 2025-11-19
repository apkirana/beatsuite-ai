/**
 * Authentication JavaScript
 * Handles login, logout, and session management
 */

// API Base URL (make it global so api.js can use it)
window.API_BASE = '/api';
const API_BASE = window.API_BASE;

// Flag to prevent redirect loops
let isRedirecting = false;

// Login form handler
document.getElementById('loginForm')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const username = document.getElementById('username').value.trim();
    const password = document.getElementById('password').value;
    const errorDiv = document.getElementById('error-message');
    const buttonText = document.getElementById('buttonText');
    const buttonSpinner = document.getElementById('buttonSpinner');
    const loginButton = document.getElementById('loginButton');
    
    // Hide error
    errorDiv.style.display = 'none';
    
    // Show loading
    buttonText.style.display = 'none';
    buttonSpinner.style.display = 'inline-block';
    loginButton.disabled = true;
    
    try {
        const response = await fetch(`${API_BASE}/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, password }),
            credentials: 'include'  // Important for cookies
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // Login successful
            console.log('Login successful:', data.user);
            
            // Store user info in sessionStorage
            sessionStorage.setItem('user', JSON.stringify(data.user));
            sessionStorage.setItem('justLoggedIn', 'true');
            
            // Set flag to prevent redirect loop
            isRedirecting = true;
            
            // Redirect to dashboard
            window.location.href = '/dashboard';
        } else {
            // Show error
            errorDiv.textContent = data.error || 'Login failed. Please try again.';
            errorDiv.style.display = 'block';
        }
    } catch (error) {
        console.error('Login error:', error);
        errorDiv.textContent = 'Connection error. Please try again.';
        errorDiv.style.display = 'block';
    } finally {
        // Reset button
        buttonText.style.display = 'inline-block';
        buttonSpinner.style.display = 'none';
        loginButton.disabled = false;
    }
});

// Logout function
async function logout() {
    try {
        await fetch(`${API_BASE}/auth/logout`, {
            method: 'POST',
            credentials: 'include'
        });
        
        // Clear session storage
        sessionStorage.removeItem('user');
        
        // Redirect to login
        window.location.href = '/login';
    } catch (error) {
        console.error('Logout error:', error);
        // Redirect anyway
        window.location.href = '/login';
    }
}

// Check authentication status
async function checkAuth() {
    try {
        const response = await fetch(`${API_BASE}/auth/check`, {
            credentials: 'include'
        });
        
        if (!response.ok) {
            console.error('Auth check failed with status:', response.status);
            return false;
        }
        
        const data = await response.json();
        console.log('Auth check result:', data);
        return data.authenticated === true;
    } catch (error) {
        console.error('Auth check error:', error);
        return false;
    }
}

// Only run auth checks after DOM is fully loaded
document.addEventListener('DOMContentLoaded', () => {
    const currentPath = window.location.pathname;
    const justLoggedIn = sessionStorage.getItem('justLoggedIn');
    
    console.log('[AUTH] DOMContentLoaded - Path:', currentPath, 'JustLoggedIn:', justLoggedIn);
    
    // Protect dashboard page
    if (currentPath === '/dashboard') {
        // If just logged in, clear the flag and allow dashboard to load
        if (justLoggedIn === 'true') {
            console.log('[AUTH] Just logged in, clearing flag - Dashboard should initialize');
            sessionStorage.removeItem('justLoggedIn');
            // Don't do any auth checks - let the dashboard load
            return;
        }
        
        // If not just logged in, verify authentication after a brief delay
        // This allows dashboard.js to start loading but catches unauthorized users
        setTimeout(() => {
            if (isRedirecting) return;
            
            console.log('[AUTH] Checking authentication status...');
            checkAuth().then(authenticated => {
                if (!authenticated && !isRedirecting) {
                    console.log('[AUTH] Not authenticated, redirecting to login');
                    isRedirecting = true;
                    sessionStorage.clear();
                    window.location.href = '/login';
                } else {
                    console.log('[AUTH] Authenticated, staying on dashboard');
                }
            });
        }, 1000);  // Increased delay to let dashboard initialize
    }
    
    // Auto-redirect from login if already authenticated  
    else if (currentPath === '/login' || currentPath === '/') {
        // Clear the just logged in flag when on login page
        sessionStorage.removeItem('justLoggedIn');
        
        setTimeout(() => {
            if (isRedirecting) return;
            
            checkAuth().then(authenticated => {
                if (authenticated && !isRedirecting) {
                    console.log('[AUTH] Already authenticated, redirecting to dashboard');
                    isRedirecting = true;
                    window.location.href = '/dashboard';
                }
            });
        }, 300);
    }
});

// Export functions for use in other scripts
window.authUtils = {
    logout,
    checkAuth
};
