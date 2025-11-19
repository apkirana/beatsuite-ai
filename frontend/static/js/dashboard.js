/**
 * Dashboard JavaScript
 * Main dashboard functionality
 */

let currentUser = null;
let rooms = [];
let refreshInterval = null;

/**
 * Initialize dashboard
 */
async function initDashboard() {
    console.log('🚀 [DASHBOARD] Initialization started');
    console.log('🔍 [DASHBOARD] window.api available?', typeof window.api !== 'undefined');
    console.log('🔍 [DASHBOARD] window.api.getCurrentUser available?', typeof window.api?.getCurrentUser === 'function');
    
    try {
        // Check if API is available
        if (!window.api) {
            throw new Error('API module not loaded');
        }
        
        // Load user info
        console.log('📡 [DASHBOARD] Fetching current user...');
        const userData = await window.api.getCurrentUser();
        console.log('✅ [DASHBOARD] User data received:', userData);
        currentUser = userData.user;  // Extract user object from response
        displayUserInfo();
        
        // Show admin button for admin users
        if (currentUser.role === 'admin') {
            document.getElementById('adminButton').style.display = 'block';
        }
        
        // Load rooms
        console.log('🏥 [DASHBOARD] Loading rooms...');
        await loadRooms();
        console.log('✅ [DASHBOARD] Rooms loaded successfully');
        
        // Check for notifications (nurses and admins)
        if (currentUser.role === 'nurse' || currentUser.role === 'admin') {
            await checkNotifications();
            // Check notifications every 30 seconds
            setInterval(checkNotifications, 30000);
        }
        
        // Start auto-refresh every 5 seconds
        refreshInterval = setInterval(loadRooms, 5000);
        
    } catch (error) {
        console.error('❌ [DASHBOARD] Initialization error:', error);
        console.error('❌ [DASHBOARD] Error stack:', error.stack);
        showError('Failed to load dashboard. Please try again.');
    }
}

/**
 * Display user info in header
 */
function displayUserInfo() {
    if (currentUser) {
        document.getElementById('userName').textContent = currentUser.username;
        document.getElementById('userRole').textContent = currentUser.role.toUpperCase();
    }
}

/**
 * Load all rooms
 */
async function loadRooms() {
    try {
        console.log('📡 Calling getRooms API...');
        const data = await window.api.getRooms();
        console.log('✅ Rooms data received:', data);
        console.log('📊 Number of rooms:', data?.rooms?.length);
        console.log('🔍 First room sample:', data?.rooms?.[0]);
        rooms = data.rooms;
        
        hideLoading();
        displayRooms();
        updateStats();
        
    } catch (error) {
        console.error('❌ Error loading rooms:', error);
        hideLoading();
        showError('Failed to load room data');
    }
}

/**
 * Display rooms in grid
 */
function displayRooms() {
    const container = document.getElementById('roomsContainer');
    
    console.log('🎨 Displaying rooms, count:', rooms.length);
    rooms.forEach((room, idx) => {
        console.log(`🏥 Room ${idx}:`, {
            room_id: room.room_id,
            room_number: room.room_number,
            patient_name: room.patient_name,
            has_vitals: !!room.vitals
        });
    });
    
    if (rooms.length === 0) {
        container.innerHTML = '<p style="text-align: center; color: #718096;">No rooms available</p>';
        return;
    }
    
    container.innerHTML = rooms.map(room => {
        // Determine health status based on vitals
        const hr = room.vitals.heart_rate;
        const spo2 = room.vitals.spo2;
        const painDetected = room.current_state.pain_detected;
        
        let healthStatus = 'stable';
        let healthIcon = '✅';
        let healthColor = '#10B981';
        let healthBg = 'rgba(16, 185, 129, 0.15)';
        
        if (painDetected || hr > 100 || spo2 < 95) {
            healthStatus = 'needs attention';
            healthIcon = '⚠️';
            healthColor = '#FFA726';
            healthBg = 'rgba(255, 167, 38, 0.15)';
        } else if (hr < 50 || hr > 110) {
            healthStatus = 'alert';
            healthIcon = '🚨';
            healthColor = '#EF5350';
            healthBg = 'rgba(239, 83, 80, 0.15)';
        }
        
        // Get AI action description
        const aiAction = getAIActionDescription(room);
        
        // Initialize assistant for this room
        setTimeout(() => initAssistant(room.room_id, room), 100);
        
        return `
        <div class="room-card">
            <div class="room-header" onclick="showRoomDetails('${room.room_id}')">
                <div class="room-header-main">
                    <div class="room-number">${room.room_number}</div>
                    <div class="patient-name">Patient: ${room.patient_name}</div>
                    <div class="health-status" style="color: ${healthColor}; background: ${healthBg}; font-weight: 700; border: 2px solid ${healthColor};">
                        ${healthIcon} ${healthStatus.toUpperCase()}
                    </div>
                </div>
                <button class="assistant-button" onclick="event.stopPropagation(); toggleAssistant('${room.room_id}')" title="AI Medical Assistant">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
                        <circle cx="9" cy="10" r="1"></circle>
                        <circle cx="15" cy="10" r="1"></circle>
                        <path d="M9.5 14.5s1 1 2.5 1 2.5-1 2.5-1"></path>
                    </svg>
                    <span>AI Assistant</span>
                </button>
            </div>
            <div class="room-body">
                <div class="vitals-grid">
                    <div class="vital-item">
                        <span class="vital-icon">
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/>
                            </svg>
                        </span>
                        <span class="vital-value">${room.vitals.heart_rate} bpm</span>
                    </div>
                    <div class="vital-item">
                        <span class="vital-icon">
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M14 14.76V3.5a2.5 2.5 0 0 0-5 0v11.26a4.5 4.5 0 1 0 5 0z"/>
                            </svg>
                        </span>
                        <span class="vital-value">${((room.vitals.temperature - 32) * 5/9).toFixed(1)}°C</span>
                    </div>
                    <div class="vital-item">
                        <span class="vital-icon">
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M9 18V5l12-2v13M9 9l12-2"/>
                                <circle cx="6" cy="18" r="3"/>
                                <circle cx="18" cy="16" r="3"/>
                            </svg>
                        </span>
                        <span class="vital-value">${room.vitals.respiratory_rate}/min</span>
                    </div>
                    <div class="vital-item">
                        <span class="vital-icon">
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M22 12h-4l-3 9L9 3l-3 9H2"/>
                            </svg>
                        </span>
                        <span class="vital-value">${room.vitals.spo2}% SpO2</span>
                    </div>
                </div>
                
                <div class="patient-state-section">
                    <span class="sleep-stage stage-${room.current_state.sleep_stage.toLowerCase().replace(' ', '-')}">
                        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
                        </svg>
                        ${room.current_state.sleep_stage}
                    </span>
                    ${painDetected ? `<span class="pain-indicator">
                        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
                            <line x1="12" y1="9" x2="12" y2="13"/>
                            <line x1="12" y1="17" x2="12.01" y2="17"/>
                        </svg>
                        Pain Detected
                    </span>` : ''}
                </div>
                
                <div class="ai-status-section">
                    <div class="ai-status-badge ${room.ai_control_active ? 'ai-active' : 'ai-override'}">
                        ${room.ai_control_active ? `
                            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
                                <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
                            </svg>
                            AI ACTIVE
                        ` : `
                            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
                                <circle cx="12" cy="7" r="4"/>
                            </svg>
                            MANUAL
                        `}
                    </div>
                    ${room.ai_control_active ? `
                        <div class="ai-actions">
                            <div class="ai-action-title">
                                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <circle cx="12" cy="12" r="10"/>
                                    <polyline points="12 6 12 12 16 14"/>
                                </svg>
                                AI Actions:
                            </div>
                            <div class="ai-action-item">
                                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <circle cx="12" cy="12" r="5"/>
                                    <line x1="12" y1="1" x2="12" y2="3"/>
                                    <line x1="12" y1="21" x2="12" y2="23"/>
                                    <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/>
                                    <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/>
                                    <line x1="1" y1="12" x2="3" y2="12"/>
                                    <line x1="21" y1="12" x2="23" y2="12"/>
                                    <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/>
                                    <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/>
                                </svg>
                                Light: ${aiAction.light}
                            </div>
                            <div class="ai-action-item">
                                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <path d="M9 18V5l12-2v13"/>
                                    <circle cx="6" cy="18" r="3"/>
                                    <circle cx="18" cy="16" r="3"/>
                                </svg>
                                Music: ${aiAction.music}
                            </div>
                            <div class="ai-reasoning">
                                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
                                </svg>
                                ${aiAction.reasoning}
                            </div>
                        </div>
                    ` : `<div class="manual-mode-text">
                        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
                            <circle cx="9" cy="7" r="4"/>
                            <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
                            <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
                        </svg>
                        Staff controlling environment
                    </div>`}
                </div>
                
                <div class="room-footer" style="margin-top: 16px; padding-top: 16px; border-top: 1px solid var(--border); display: flex; gap: 8px;">
                    <button class="view-history-btn" onclick="event.stopPropagation(); showHealthHistory('${room.patient_id}', '${room.patient_name}')" title="View Health History">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <line x1="12" y1="20" x2="12" y2="10"/>
                            <line x1="18" y1="20" x2="18" y2="4"/>
                            <line x1="6" y1="20" x2="6" y2="16"/>
                        </svg>
                        <span>View History</span>
                    </button>
                    <button class="generate-report-btn" onclick="event.stopPropagation(); generatePatientReport('${room.room_id}')" title="Generate PDF Report">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                            <polyline points="14 2 14 8 20 8"/>
                            <line x1="16" y1="13" x2="8" y2="13"/>
                            <line x1="16" y1="17" x2="8" y2="17"/>
                            <polyline points="10 9 9 9 8 9"/>
                        </svg>
                        <span>Report</span>
                    </button>
                </div>
            </div>
        </div>
        `;
    }).join('');
    
    // Create assistant modals and append to body
    rooms.forEach(room => {
        createAssistantModal(room);
    });
}

/**
 * Create assistant modal for a room and append to body
 */
function createAssistantModal(room) {
    // Remove existing modal if any
    const existingModal = document.getElementById(`assistant-modal-${room.room_id}`);
    if (existingModal) {
        existingModal.remove();
    }
    
    const modalHTML = `
        <div id="assistant-modal-${room.room_id}" class="assistant-modal-overlay" style="display: none;">
            <div class="assistant-modal-content">
                <div class="assistant-modal-header">
                    <div class="assistant-modal-title">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
                            <circle cx="9" cy="10" r="1"></circle>
                            <circle cx="15" cy="10" r="1"></circle>
                            <path d="M9.5 14.5s1 1 2.5 1 2.5-1 2.5-1"></path>
                        </svg>
                        <span>AI Medical Assistant - ${room.patient_name}</span>
                    </div>
                    <button class="assistant-close-btn" onclick="event.stopPropagation(); toggleAssistant('${room.room_id}')">&times;</button>
                </div>
                <div id="chat-messages-${room.room_id}" class="assistant-chat-messages">
                    <div class="assistant-message system">
                        <div style="text-align: center; padding: 30px 20px;">
                            <div style="width: 80px; height: 80px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 20px; box-shadow: 0 8px 24px rgba(102, 126, 234, 0.3);">
                                <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2">
                                    <circle cx="12" cy="12" r="10"></circle>
                                    <path d="M8 14s1.5 2 4 2 4-2 4-2"></path>
                                    <line x1="9" y1="9" x2="9.01" y2="9"></line>
                                    <line x1="15" y1="9" x2="15.01" y2="9"></line>
                                </svg>
                            </div>
                            <div style="font-size: 22px; font-weight: 700; color: #1E293B; margin-bottom: 8px;">
                                Gemini Live Assistant
                            </div>
                            <div style="font-size: 15px; color: #667eea; margin-bottom: 16px; font-weight: 600;">
                                for ${room.patient_name}
                            </div>
                            <div style="font-size: 14px; color: #64748B; line-height: 1.8; max-width: 400px; margin: 0 auto;">
                                Experience natural, real-time voice conversations with AI. Just click <strong>"Start Live Chat"</strong> below and speak naturally about vitals, sleep status, pain levels, or care needs.
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Gemini Live Voice Assistant -->
                <div class="gemini-live-section" style="margin: 20px; padding: 24px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 16px; box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);">
                    <div style="display: flex; align-items: center; gap: 16px; margin-bottom: 20px;">
                        <div style="width: 56px; height: 56px; background: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
                            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#667eea" stroke-width="2.5">
                                <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path>
                                <path d="M19 10v2a7 7 0 0 1-14 0v-2"></path>
                                <line x1="12" y1="19" x2="12" y2="23"></line>
                                <line x1="8" y1="23" x2="16" y2="23"></line>
                            </svg>
                        </div>
                        <div style="flex: 1;">
                            <div style="font-weight: 700; color: white; font-size: 18px; margin-bottom: 4px; letter-spacing: -0.5px;">Gemini Live</div>
                            <div style="font-size: 13px; color: rgba(255,255,255,0.9); font-weight: 500;">Real-time AI voice conversation</div>
                        </div>
                        <span id="gemini-live-status-${room.room_id}" style="color: white; font-size: 12px; background: rgba(255,255,255,0.2); padding: 6px 12px; border-radius: 20px; font-weight: 600; backdrop-filter: blur(10px);">⚪ Inactive</span>
                    </div>
                    <button id="gemini-live-toggle-${room.room_id}" class="gemini-live-btn" onclick="event.stopPropagation(); window.toggleGeminiLive('${room.room_id}')" style="width: 100%; padding: 16px; background: white; color: #667eea; border: none; border-radius: 12px; font-weight: 700; cursor: pointer; transition: all 0.3s; box-shadow: 0 4px 16px rgba(0,0,0,0.15); font-size: 16px; display: flex; align-items: center; justify-content: center; gap: 10px;">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                            <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path>
                            <path d="M19 10v2a7 7 0 0 1-14 0v-2"></path>
                            <line x1="12" y1="19" x2="12" y2="23"></line>
                            <line x1="8" y1="23" x2="16" y2="23"></line>
                        </svg>
                        <span>Start Voice Chat</span>
                    </button>
                    <div style="margin-top: 16px; padding: 12px; background: rgba(255,255,255,0.1); border-radius: 10px; backdrop-filter: blur(10px);">
                        <div style="font-size: 12px; color: rgba(255,255,255,0.95); line-height: 1.6;">
                            💡 <strong>Tip:</strong> Speak naturally about patient vitals, comfort, sleep quality, or care needs. Gemini will respond with voice in real-time.
                        </div>
                    </div>
                    <div id="gemini-live-transcript-${room.room_id}" class="gemini-live-transcript" style="display: none; margin-top: 16px; max-height: 250px; overflow-y: auto; background: rgba(0,0,0,0.25); border-radius: 10px; padding: 12px; backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,0.1);"></div>
                </div>
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', modalHTML);
    
    // Add proper click handler to close only when clicking the overlay background
    const modalOverlay = document.getElementById(`assistant-modal-${room.room_id}`);
    const modalContent = modalOverlay?.querySelector('.assistant-modal-content');
    const chatMessages = document.getElementById(`chat-messages-${room.room_id}`);
    const inputField = document.getElementById(`assistant-input-${room.room_id}`);
    
    if (modalOverlay) {
        // Close only when clicking the dark overlay background
        modalOverlay.addEventListener('click', function(event) {
            // Don't close if mic permission is being requested
            if (modalOverlay.dataset.micRequesting === 'true') {
                console.log('🔒 Modal LOCKED - microphone permission in progress');
                event.stopPropagation();
                event.preventDefault();
                return;
            }
            
            // Don't close if assistant is actively listening
            const assistant = window.assistants && window.assistants[room.room_id];
            if (assistant && assistant.isListening) {
                console.log('🎤 Assistant is listening - modal stays open (click ignored)');
                event.stopPropagation();
                event.preventDefault();
                return;
            }
            
            if (event.target === modalOverlay) {
                console.log('📍 Overlay clicked - toggling modal');
                toggleAssistant(room.room_id);
            }
        });
    }
    
    // Prevent all events from bubbling out of modal content
    if (modalContent) {
        modalContent.addEventListener('click', function(event) {
            event.stopPropagation();
        });
        
        // Also prevent on buttons specifically
        const allButtons = modalContent.querySelectorAll('button');
        allButtons.forEach(btn => {
            btn.addEventListener('click', function(e) {
                e.stopPropagation();
            });
        });
    }
    
    // Prevent scroll events from bubbling
    if (chatMessages) {
        chatMessages.addEventListener('wheel', function(event) {
            event.stopPropagation();
        });
        chatMessages.addEventListener('touchmove', function(event) {
            event.stopPropagation();
        });
    }
    
    // Prevent input field events from causing issues
    if (inputField) {
        inputField.addEventListener('click', function(event) {
            event.stopPropagation();
        });
        inputField.addEventListener('focus', function(event) {
            event.stopPropagation();
        });
        inputField.addEventListener('input', function(event) {
            event.stopPropagation();
        });
    }
}

/**
 * Get AI action description based on room environment
 */
function getAIActionDescription(room) {
    const env = room.environment || {};
    const sleepStage = room.current_state.sleep_stage || 'AWAKE';
    const painDetected = room.current_state.pain_detected || false;
    
    // Determine light description
    let lightDesc = '';
    const brightness = Math.round((env.light_brightness || 0.5) * 100);
    const lightColor = env.light_hex_color || '#FFFFFF';
    
    if (brightness <= 10) {
        lightDesc = `Dim (${brightness}%)`;
    } else if (brightness <= 40) {
        lightDesc = `Low (${brightness}%)`;
    } else if (brightness <= 70) {
        lightDesc = `Medium (${brightness}%)`;
    } else {
        lightDesc = `Bright (${brightness}%)`;
    }
    
    // Add color description
    if (lightColor.toLowerCase().includes('ff6') || lightColor.toLowerCase().includes('ff7')) {
        lightDesc += ', Red therapy';
    } else if (lightColor.toLowerCase().includes('ffa') || lightColor.toLowerCase().includes('ffb')) {
        lightDesc += ', Amber';
    } else if (lightColor.toLowerCase().includes('ffd') || lightColor.toLowerCase().includes('ffe')) {
        lightDesc += ', Warm';
    } else if (lightColor.toLowerCase().includes('e0f') || lightColor.toLowerCase().includes('e8f')) {
        lightDesc += ', Blue-enriched';
    } else {
        lightDesc += ', Neutral';
    }
    
    // Determine music description
    let musicDesc = '';
    const volume = Math.round((env.music_volume || 0.2) * 100);
    const playlist = env.music_playlist_id || 'calm_ambient';
    
    if (playlist.includes('sleep') || playlist.includes('binaural')) {
        musicDesc = `Sleep therapy (${volume}%)`;
    } else if (playlist.includes('healing') || playlist.includes('pain')) {
        musicDesc = `Healing frequencies (${volume}%)`;
    } else if (playlist.includes('upbeat') || playlist.includes('morning')) {
        musicDesc = `Energizing (${volume}%)`;
    } else if (playlist.includes('calm') || playlist.includes('ambient')) {
        musicDesc = `Calming (${volume}%)`;
    } else {
        musicDesc = `Ambient (${volume}%)`;
    }
    
    // Generate reasoning based on patient state
    let reasoning = '';
    if (painDetected) {
        reasoning = '🔴 Applying pain relief therapy';
    } else if (sleepStage.includes('DEEP')) {
        reasoning = '💤 Supporting deep sleep recovery';
    } else if (sleepStage.includes('LIGHT') || sleepStage.includes('REM')) {
        reasoning = '😴 Maintaining sleep environment';
    } else if (sleepStage.includes('AWAKE')) {
        const hour = new Date().getHours();
        if (hour >= 6 && hour < 12) {
            reasoning = '☀️ Morning wake-up support';
        } else if (hour >= 12 && hour < 18) {
            reasoning = '☀️ Optimal daytime environment';
        } else if (hour >= 18 && hour < 22) {
            reasoning = '🌙 Evening relaxation mode';
        } else {
            reasoning = '🌙 Nighttime rest preparation';
        }
    } else {
        reasoning = '🤖 Optimizing patient comfort';
    }
    
    return {
        light: lightDesc,
        music: musicDesc,
        reasoning: reasoning
    };
}

/**
 * Update stats cards
 */
function updateStats() {
    const totalRooms = rooms.length;
    const activeAI = rooms.filter(r => r.ai_control_active).length;
    const sleeping = rooms.filter(r => r.current_state.sleep_stage !== 'AWAKE').length;
    const alerts = rooms.filter(r => r.current_state.pain_detected).length;
    
    document.getElementById('totalRooms').textContent = totalRooms;
    document.getElementById('activeAI').textContent = activeAI;
    document.getElementById('sleeping').textContent = sleeping;
    document.getElementById('alerts').textContent = alerts;
}

/**
 * Show room details modal
 */
async function showRoomDetails(roomId) {
    try {
        const data = await window.api.getRoomData(roomId);
        const room = data.room;
        
        document.getElementById('modalTitle').textContent = `${room.room_number} - ${room.patient_name}`;
        
        document.getElementById('modalBody').innerHTML = `
            <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px;">
                <div>
                    <h3 style="margin-bottom: 15px;">Vital Signs</h3>
                    <div style="display: grid; gap: 10px;">
                        <div><strong>Heart Rate:</strong> ${room.vitals.heart_rate} bpm</div>
                        <div><strong>Temperature:</strong> ${((room.vitals.temperature - 32) * 5/9).toFixed(1)}°C</div>
                        <div><strong>Respiratory Rate:</strong> ${room.vitals.respiratory_rate}/min</div>
                        <div><strong>SpO2:</strong> ${room.vitals.spo2}%</div>
                        <div><strong>Blood Pressure:</strong> ${room.vitals.blood_pressure}</div>
                    </div>
                </div>
                
                <div>
                    <h3 style="margin-bottom: 15px;">Current State</h3>
                    <div style="display: grid; gap: 10px;">
                        <div><strong>Sleep Stage:</strong> ${room.current_state.sleep_stage}</div>
                        <div><strong>Pain Detected:</strong> ${room.current_state.pain_detected ? '⚠️ Yes' : '✅ No'}</div>
                        <div><strong>Movement:</strong> ${room.current_state.movement_level}</div>
                        <div><strong>AI Control:</strong> ${room.ai_control_active ? '✅ Active' : '⏸️ Paused'}</div>
                    </div>
                </div>
                
                <div>
                    <h3 style="margin-bottom: 15px;">Environment</h3>
                    <div style="display: grid; gap: 10px;">
                        <div><strong>Light Level:</strong> ${room.environment.light_level}%</div>
                        <div><strong>Light Color:</strong> ${room.environment.light_color} K</div>
                        <div><strong>Music Volume:</strong> ${room.environment.music_volume}%</div>
                        <div><strong>Music Type:</strong> ${room.environment.music_type}</div>
                    </div>
                </div>
                
                <div>
                    <h3 style="margin-bottom: 15px;">AI Insights</h3>
                    <div style="display: grid; gap: 10px; font-size: 13px;">
                        <div>${room.ai_insights.sleep_quality}</div>
                        <div>${room.ai_insights.circadian_status}</div>
                    </div>
                </div>
            </div>
            
            <div style="margin-top: 25px; padding-top: 20px; border-top: 1px solid #e2e8f0;">
                <button onclick="toggleAI('${room.room_id}', ${room.ai_control_active})" 
                        class="logout-button" 
                        style="background: ${room.ai_control_active ? '#ed8936' : '#48bb78'}; width: auto;">
                    ${room.ai_control_active ? 'Pause AI Control' : 'Resume AI Control'}
                </button>
            </div>
        `;
        
        document.getElementById('roomModal').style.display = 'flex';
        
    } catch (error) {
        console.error('Error loading room details:', error);
        alert('Failed to load room details');
    }
}

/**
 * Toggle AI control
 */
async function toggleAI(roomId, isActive) {
    try {
        console.log(`[TOGGLE AI] Room: ${roomId}, Currently Active: ${isActive}`);
        
        const API_BASE = window.API_BASE || '/api';
        let response;
        
        if (isActive) {
            // Pause AI - set manual override
            console.log('[TOGGLE AI] Pausing AI control...');
            response = await fetch(`${API_BASE}/rooms/${roomId}/override`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                credentials: 'include',
                body: JSON.stringify({
                    brightness: 50,
                    volume: 30
                })
            });
        } else {
            // Resume AI control
            console.log('[TOGGLE AI] Resuming AI control...');
            response = await fetch(`${API_BASE}/rooms/${roomId}/resume`, {
                method: 'POST',
                credentials: 'include'
            });
        }
        
        const data = await response.json();
        console.log('[TOGGLE AI] Response:', data);
        
        if (data.success) {
            alert(data.message);
            closeModal();
            await loadRooms();
        } else {
            alert('Failed: ' + (data.error || 'Unknown error'));
        }
        
    } catch (error) {
        console.error('❌ Error toggling AI:', error);
        alert('Failed to toggle AI control');
    }
}

/**
 * Close modal
 */
function closeModal() {
    document.getElementById('roomModal').style.display = 'none';
}

/**
 * Show error message
 */
function showError(message) {
    document.getElementById('errorText').textContent = message;
    document.getElementById('errorMessage').style.display = 'block';
}

/**
 * Hide loading indicator
 */
function hideLoading() {
    document.getElementById('loadingIndicator').style.display = 'none';
}

/**
 * Check for critical patient notifications
 */
async function checkNotifications() {
    try {
        const API_BASE = window.API_BASE || '/api';
        const response = await fetch(`${API_BASE}/notifications/unread`, {
            credentials: 'include'
        });
        
        if (!response.ok) return;
        
        const data = await response.json();
        
        if (data.success && data.count > 0) {
            // Show notifications
            displayNotifications(data.notifications);
        }
    } catch (error) {
        console.error('Error checking notifications:', error);
    }
}

/**
 * Display critical notifications
 */
function displayNotifications(notifications) {
    // Create notification container if it doesn't exist
    let container = document.getElementById('notificationContainer');
    
    if (!container) {
        container = document.createElement('div');
        container.id = 'notificationContainer';
        container.style.cssText = `
            position: fixed;
            top: 80px;
            right: 20px;
            z-index: 1000;
            max-width: 400px;
        `;
        document.body.appendChild(container);
    }
    
    // Clear old notifications
    container.innerHTML = '';
    
    // Show each notification
    notifications.forEach(notif => {
        const notifDiv = document.createElement('div');
        notifDiv.className = 'notification-alert';
        notifDiv.style.cssText = `
            background: #fff;
            border-left: 4px solid #f56565;
            padding: 16px;
            margin-bottom: 12px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
            animation: slideIn 0.3s ease-out;
        `;
        
        notifDiv.innerHTML = `
            <div style="display: flex; justify-content: space-between; align-items: start;">
                <div style="flex: 1;">
                    <div style="font-weight: 600; color: #c53030; margin-bottom: 4px;">
                        🚨 CRITICAL ALERT
                    </div>
                    <div style="color: #333; font-size: 14px;">
                        ${notif.message}
                    </div>
                    <div style="color: #666; font-size: 12px; margin-top: 4px;">
                        ${new Date(notif.created_at).toLocaleString()}
                    </div>
                </div>
                <button onclick="dismissNotification('${notif.id}')" 
                        style="background: none; border: none; font-size: 20px; cursor: pointer; color: #999;">
                    ×
                </button>
            </div>
        `;
        
        container.appendChild(notifDiv);
        
        // Auto-dismiss after 30 seconds
        setTimeout(() => {
            if (notifDiv.parentNode) {
                notifDiv.style.animation = 'slideOut 0.3s ease-in';
                setTimeout(() => notifDiv.remove(), 300);
            }
        }, 30000);
    });
}

/**
 * Dismiss a notification
 */
async function dismissNotification(notificationId) {
    try {
        const API_BASE = window.API_BASE || '/api';
        await fetch(`${API_BASE}/notifications/${notificationId}/read`, {
            method: 'POST',
            credentials: 'include'
        });
        
        // Remove from UI
        const notifElements = document.querySelectorAll('.notification-alert');
        notifElements.forEach(el => {
            if (el.innerHTML.includes(notificationId)) {
                el.style.animation = 'slideOut 0.3s ease-in';
                setTimeout(() => el.remove(), 300);
            }
        });
    } catch (error) {
        console.error('Error dismissing notification:', error);
    }
}

// Add CSS animations
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

// Initialize on page load
document.addEventListener('DOMContentLoaded', initDashboard);

// Navigate to admin page
function goToAdmin() {
    window.location.href = '/admin';
}

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (refreshInterval) {
        clearInterval(refreshInterval);
    }
});

/**
 * Toggle AI Assistant modal
 */
window.toggleAssistant = function(roomId, forceOpen = false) {
    const modal = document.getElementById(`assistant-modal-${roomId}`);
    
    if (!modal) {
        console.error('❌ Modal not found for room:', roomId);
        return;
    }
    
    // Don't close if microphone permission is being requested
    if (modal.dataset.micRequesting === 'true') {
        console.log('🔒 Modal LOCKED - microphone permission in progress, cannot close');
        return;
    }
    
    // Check if assistant is listening - don't close if actively listening
    const assistant = window.assistants && window.assistants[roomId];
    if (assistant && assistant.isListening && !forceOpen) {
        console.log('🎤 Assistant is listening - modal stays open');
        return;
    }
    
    console.log('🔄 Toggle assistant for room:', roomId, 'Current display:', modal.style.display, 'Force open:', forceOpen);
    
    // Close any open modals first
    const allModals = document.querySelectorAll('.assistant-modal-overlay');
    allModals.forEach(m => {
        if (m.id !== `assistant-modal-${roomId}`) {
            m.style.display = 'none';
            // Stop any ongoing speech
            const modalRoomId = m.id.replace('assistant-modal-', '');
            if (window.assistants && window.assistants[modalRoomId]) {
                window.assistants[modalRoomId].stopSpeaking();
            }
        }
    });
    
    if (modal.style.display === 'none' || modal.style.display === '' || forceOpen) {
        console.log('✅ Opening modal for room:', roomId);
        modal.style.display = 'flex';
        // Scroll to bottom of chat
        const chatMessages = document.getElementById(`chat-messages-${roomId}`);
        if (chatMessages) {
            setTimeout(() => {
                chatMessages.scrollTop = chatMessages.scrollHeight;
            }, 100);
        }
    } else {
        console.log('❌ Closing modal for room:', roomId);
        modal.style.display = 'none';
        // Stop any ongoing speech and listening
        if (assistant) {
            assistant.stopSpeaking();
            if (assistant.isListening) {
                assistant.toggleVoiceInput();
            }
        }
    }
};

/**
 * Handle text query from assistant
 */
window.handleAssistantQuery = function(roomId, event) {
    if (event) {
        event.stopPropagation();
        event.preventDefault();
    }
    const input = document.getElementById(`assistant-input-${roomId}`);
    if (input && input.value.trim()) {
        const query = input.value.trim();
        input.value = '';
        
        if (window.assistants && window.assistants[roomId]) {
            window.assistants[roomId].handleUserQuery(query);
        }
    }
};

/**
 * Toggle voice input
 */
window.toggleVoiceInput = function(roomId, event) {
    if (event) {
        event.stopPropagation();
        event.preventDefault();
    }
    
    console.log('🎤 Toggle voice input for room:', roomId);
    
    // Lock the modal immediately before starting voice input
    const modal = document.getElementById(`assistant-modal-${roomId}`);
    const assistant = window.assistants && window.assistants[roomId];
    
    if (modal && modal.style.display !== 'none') {
        // If starting to listen, lock the modal
        if (assistant && !assistant.isListening) {
            modal.dataset.micRequesting = 'true';
            console.log('🔒 Modal LOCKED - starting microphone');
            
            // Auto-unlock after 10 seconds as safety measure (increased from 5)
            setTimeout(() => {
                if (modal.dataset.micRequesting === 'true') {
                    delete modal.dataset.micRequesting;
                    console.log('🔓 Modal auto-unlocked after timeout');
                }
            }, 10000);
        } else if (assistant && assistant.isListening) {
            // If stopping, unlock the modal
            delete modal.dataset.micRequesting;
            console.log('🔓 Modal unlocked - stopping microphone');
        }
    }
    
    if (assistant) {
        assistant.toggleVoiceInput();
    }
};

/**
 * Toggle speaker (mute/unmute)
 */
window.toggleSpeaker = function(roomId, event) {
    if (event) {
        event.stopPropagation();
        event.preventDefault();
    }
    const assistant = window.assistants && window.assistants[roomId];
    if (assistant) {
        assistant.isMuted = !assistant.isMuted;
        const speakerBtn = document.getElementById(`assistant-speaker-${roomId}`);
        if (speakerBtn) {
            if (assistant.isMuted) {
                speakerBtn.classList.add('muted');
                speakerBtn.textContent = '🔇';
                assistant.stopSpeaking();
            } else {
                speakerBtn.classList.remove('muted');
                speakerBtn.textContent = '🔊';
            }
        }
    }
};

/**
 * Initialize assistant for a room
 */
window.initAssistant = function(roomId, roomData) {
    if (typeof SmartAssistant === 'undefined') {
        console.warn('SmartAssistant class not loaded yet for room:', roomId);
        return;
    }
    
    if (!window.assistants) {
        window.assistants = {};
    }
    
    try {
        window.assistants[roomId] = new SmartAssistant(roomId, roomData);
        console.log('✅ Assistant initialized for room:', roomId);
    } catch (error) {
        console.error('Error initializing assistant for room:', roomId, error);
    }
};

/**
 * Toggle Gemini Live for a room
 */
window.toggleGeminiLive = function(roomId) {
    console.log('🎯 toggleGeminiLive called for room:', roomId);
    
    // Check if GeminiLive class is available
    if (typeof GeminiLive === 'undefined') {
        console.error('❌ GeminiLive class not loaded!');
        alert('Error: Gemini Live feature not loaded. Please refresh the page.');
        return;
    }
    
    // Initialize Gemini Live instances if not exists
    if (!window.geminiLiveInstances) {
        window.geminiLiveInstances = {};
        console.log('✅ Initialized geminiLiveInstances');
    }
    
    // Get or create Gemini Live instance
    if (!window.geminiLiveInstances[roomId]) {
        console.log('📝 Creating new Gemini Live instance for room:', roomId);
        // Get room data from current rooms
        const roomCard = document.querySelector(`[data-room-id="${roomId}"]`);
        if (!roomCard) {
            console.error('Room data not found for:', roomId);
            return;
        }
        
        // Get room data from window.currentRooms
        const roomData = window.currentRooms?.find(r => r.room_id === roomId);
        if (!roomData) {
            console.error('Room data not found in currentRooms:', roomId);
            return;
        }
        
        // Create new Gemini Live instance
        console.log('🔧 Creating GeminiLive instance with data:', roomData);
        window.geminiLiveInstances[roomId] = new GeminiLive(roomId, roomData);
        console.log('✅ GeminiLive instance created');
        
        // Override updateUI to use our specific elements
        const instance = window.geminiLiveInstances[roomId];
        const originalUpdateUI = instance.updateUI.bind(instance);
        instance.updateUI = function(state, message = '') {
            const statusEl = document.getElementById(`gemini-live-status-${roomId}`);
            const buttonEl = document.getElementById(`gemini-live-toggle-${roomId}`);
            const transcriptEl = document.getElementById(`gemini-live-transcript-${roomId}`);
            
            if (statusEl) {
                let icon = '⚪';
                let color = 'rgba(255,255,255,0.7)';
                
                switch (state) {
                    case 'active':
                        icon = '🟢';
                        color = 'rgba(16, 185, 129, 1)';
                        message = message || 'Connected';
                        break;
                    case 'listening':
                        icon = '🎤';
                        color = 'rgba(59, 130, 246, 1)';
                        break;
                    case 'speaking':
                        icon = '🔊';
                        color = 'rgba(139, 92, 246, 1)';
                        break;
                    case 'error':
                        icon = '❌';
                        color = 'rgba(239, 68, 68, 1)';
                        break;
                    default:
                        icon = '⚪';
                        message = 'Inactive';
                }
                
                statusEl.innerHTML = `${icon} ${message}`;
                statusEl.style.color = color;
            }
            
            if (buttonEl) {
                if (this.isActive) {
                    buttonEl.innerHTML = `
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                            <rect x="6" y="4" width="4" height="16"></rect>
                            <rect x="14" y="4" width="4" height="16"></rect>
                        </svg>
                        <span>Stop Voice Chat</span>
                    `;
                    buttonEl.style.background = '#ef4444';
                    buttonEl.style.color = 'white';
                    buttonEl.classList.add('active');
                } else {
                    buttonEl.innerHTML = `
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                            <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path>
                            <path d="M19 10v2a7 7 0 0 1-14 0v-2"></path>
                            <line x1="12" y1="19" x2="12" y2="23"></line>
                            <line x1="8" y1="23" x2="16" y2="23"></line>
                        </svg>
                        <span>Start Voice Chat</span>
                    `;
                    buttonEl.style.background = 'white';
                    buttonEl.style.color = '#667eea';
                    buttonEl.classList.remove('active');
                }
            }
            
            // Show/hide transcript
            if (transcriptEl && this.isActive) {
                transcriptEl.style.display = 'block';
            } else if (transcriptEl) {
                transcriptEl.style.display = 'none';
            }
        };
        
        // Override displayTranscript to use our specific element
        instance.displayTranscript = function(speaker, text) {
            const transcriptEl = document.getElementById(`gemini-live-transcript-${roomId}`);
            if (transcriptEl) {
                const messageEl = document.createElement('div');
                messageEl.style.cssText = `
                    padding: 6px 8px;
                    margin-bottom: 4px;
                    border-radius: 6px;
                    font-size: 12px;
                    background: ${speaker === 'AI' ? 'rgba(139, 92, 246, 0.3)' : 'rgba(59, 130, 246, 0.3)'};
                    color: white;
                `;
                messageEl.innerHTML = `<strong>${speaker}:</strong> ${text}`;
                transcriptEl.appendChild(messageEl);
                transcriptEl.scrollTop = transcriptEl.scrollHeight;
            }
        };
    }
    
    // Toggle the instance
    console.log('🔄 Calling toggle on instance:', window.geminiLiveInstances[roomId]);
    window.geminiLiveInstances[roomId].toggle();
    console.log('✅ Toggle completed');
};

// Export functions for inline onclick handlers
window.showRoomDetails = showRoomDetails;
window.closeModal = closeModal;
window.toggleAI = toggleAI;
window.dismissNotification = dismissNotification;
