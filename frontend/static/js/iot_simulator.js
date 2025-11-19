/**
 * IoT Device Simulator
 * Real-time visualization of smart lights and audio systems with REAL AUDIO
 */

let rooms = [];
let refreshInterval = null;
let audioPlayers = {}; // Store Howler instances for each room

// Music playlist names and actual audio sources (royalty-free)
const PLAYLISTS = {
    'calm_ambient': {
        name: 'Calm Ambient',
        url: 'https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3',
        description: 'Relaxing ambient sounds'
    },
    'soft_instrumental': {
        name: 'Soft Instrumental',
        url: 'https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3',
        description: 'Gentle instrumental music'
    },
    'upbeat_morning': {
        name: 'Upbeat Morning',
        url: 'https://www.soundhelix.com/examples/mp3/SoundHelix-Song-3.mp3',
        description: 'Energetic morning tunes'
    },
    'children_playful': {
        name: "Children's Playful",
        url: 'https://www.soundhelix.com/examples/mp3/SoundHelix-Song-4.mp3',
        description: 'Fun and playful music'
    },
    'disney_classics': {
        name: 'Disney Classics',
        url: 'https://www.soundhelix.com/examples/mp3/SoundHelix-Song-5.mp3',
        description: 'Classic Disney-style music'
    },
    'nature_sounds': {
        name: 'Nature Sounds',
        url: 'https://www.soundhelix.com/examples/mp3/SoundHelix-Song-6.mp3',
        description: 'Calming nature ambience'
    },
    'classical_piano': {
        name: 'Classical Piano',
        url: 'https://www.soundhelix.com/examples/mp3/SoundHelix-Song-7.mp3',
        description: 'Classical piano pieces'
    },
    'meditation': {
        name: 'Meditation',
        url: 'https://www.soundhelix.com/examples/mp3/SoundHelix-Song-8.mp3',
        description: 'Deep meditation music'
    }
};

/**
 * Initialize simulator
 */
async function initSimulator() {
    console.log('🎮 IoT Simulator initializing...');
    
    try {
        await loadRooms();
        
        // Refresh every 3 seconds
        refreshInterval = setInterval(loadRooms, 3000);
        
        console.log('✅ IoT Simulator ready');
    } catch (error) {
        console.error('❌ Failed to initialize simulator:', error);
        showError(error.message);
    }
}

/**
 * Load rooms data
 */
async function loadRooms() {
    try {
        const response = await window.api.getRooms();
        rooms = response.rooms;
        displayRooms();
    } catch (error) {
        console.error('Error loading rooms:', error);
        showError('Failed to load room data');
    }
}

/**
 * Display all rooms with IoT simulators
 */
function displayRooms() {
    const container = document.getElementById('roomsContainer');
    
    if (!rooms || rooms.length === 0) {
        container.innerHTML = `
            <div class="loading-container">
                <div class="loading-spinner"></div>
                <p>Loading IoT devices...</p>
            </div>
        `;
        return;
    }
    
    container.innerHTML = rooms.map(room => createRoomSimulator(room)).join('');
}

/**
 * Create IoT simulator for a room
 */
function createRoomSimulator(room) {
    const env = room.environment || {};
    const lightColor = env.light_hex_color || '#FFFFFF';
    const brightness = (env.light_brightness || 0.5) * 100;
    const playlist = env.music_playlist_id || 'none';
    const volume = (env.music_volume || 0.3) * 100;
    const aiReasoning = env.ai_reasoning || 'Monitoring patient condition...';
    const isAIActive = room.ai_control_active;
    
    const playlistData = PLAYLISTS[playlist] || { name: 'No Music', url: null };
    const playlistName = playlistData.name;
    const isPlaying = playlist !== 'none' && isAIActive;
    
    // Initialize or update audio player for this room
    if (playlistData.url && isPlaying) {
        initAudioPlayer(room.room_id, playlistData.url, volume / 100);
    } else if (audioPlayers[room.room_id]) {
        stopAudioPlayer(room.room_id);
    }
    
    return `
        <div class="room-simulator">
            <div class="room-header">
                <div>
                    <div class="room-title">${room.room_number}</div>
                    <div class="room-patient">${room.patient_name}</div>
                </div>
                <div class="ai-badge ${isAIActive ? 'active' : 'manual'}">
                    ${isAIActive ? '🤖 AI Control' : '👤 Manual'}
                </div>
            </div>
            
            <!-- AI Reasoning - Prominent Position -->
            ${isAIActive ? `
                <div class="ai-reasoning-box">
                    <div class="reasoning-title">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                            <circle cx="12" cy="12" r="10"/>
                            <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/>
                            <line x1="12" y1="17" x2="12.01" y2="17"/>
                        </svg>
                        AI Decision Reasoning
                    </div>
                    <div class="reasoning-text">${aiReasoning}</div>
                </div>
            ` : ''}
            
            <!-- Smart Lamp Simulator -->
            <div class="device-section">
                <div class="device-title">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
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
                    Smart Lighting System
                </div>
                
                <div class="lamp-container">
                    <div class="lamp-glow" style="background: ${lightColor}; opacity: ${brightness / 150};"></div>
                    <div class="lamp-bulb" style="background: ${lightColor}; box-shadow: 0 0 ${brightness}px ${lightColor};">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M9 18h6"/>
                            <path d="M10 22h4"/>
                            <path d="M15 2a5 5 0 00-6 4.9V14a2 2 0 002 2h2a2 2 0 002-2V6.9A5 5 0 0015 2z"/>
                        </svg>
                    </div>
                </div>
                
                <div class="lamp-info">
                    <div class="lamp-details">
                        <div class="lamp-detail-item">
                            <span class="lamp-detail-label">Color</span>
                            <span class="lamp-detail-value">${lightColor}</span>
                        </div>
                        <div class="lamp-detail-item">
                            <span class="lamp-detail-label">Brightness</span>
                            <span class="lamp-detail-value">${Math.round(brightness)}%</span>
                        </div>
                        <div class="lamp-detail-item">
                            <span class="lamp-detail-label">Status</span>
                            <span class="lamp-detail-value">${brightness > 5 ? '🟢 ON' : '⚫ OFF'}</span>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Music Player Simulator -->
            <div class="device-section">
                <div class="device-title">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M9 18V5l12-2v13"/>
                        <circle cx="6" cy="18" r="3"/>
                        <circle cx="18" cy="16" r="3"/>
                    </svg>
                    Smart Audio System
                </div>
                
                <div class="music-player">
                    <div class="music-status">
                        <div class="music-icon-container ${isPlaying ? 'playing' : ''}" 
                             onclick="toggleAudio('${room.room_id}')" 
                             style="cursor: pointer;" 
                             title="Click to play/pause">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <polygon points="5 3 19 12 5 21 5 3"/>
                            </svg>
                        </div>
                        
                        <div class="music-info">
                            <div class="music-playlist">${playlistName}</div>
                            <div class="music-state" id="musicState_${room.room_id}">
                                ${isPlaying ? '▶️ Playing' : '⏸️ Paused'}
                            </div>
                            ${playlistData.description ? `<div style="font-size: 10px; color: rgba(255,255,255,0.5); margin-top: 2px;">${playlistData.description}</div>` : ''}
                        </div>
                    </div>
                    
                    <!-- Manual Audio Controls -->
                    ${playlistData.url ? `
                        <div class="audio-controls">
                            <button onclick="toggleAudio('${room.room_id}')" class="control-btn" title="Play/Pause">
                                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <polygon points="5 3 19 12 5 21 5 3"/>
                                </svg>
                            </button>
                            <button onclick="stopAudioPlayer('${room.room_id}')" class="control-btn" title="Stop">
                                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <rect x="6" y="6" width="12" height="12"/>
                                </svg>
                            </button>
                            <button onclick="adjustVolume('${room.room_id}', -10)" class="control-btn" title="Volume Down">
                                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/>
                                    <line x1="23" y1="9" x2="17" y2="15"/>
                                    <line x1="17" y1="9" x2="23" y2="15"/>
                                </svg>
                            </button>
                            <button onclick="adjustVolume('${room.room_id}', 10)" class="control-btn" title="Volume Up">
                                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/>
                                    <path d="M19.07 4.93a10 10 0 0 1 0 14.14M15.54 8.46a5 5 0 0 1 0 7.07"/>
                                </svg>
                            </button>
                        </div>
                    ` : ''}
                    </div>
                    
                    <div class="volume-control">
                        <span class="volume-label">Volume:</span>
                        <div class="volume-bar">
                            <div class="volume-fill" style="width: ${volume}%;"></div>
                        </div>
                        <span class="volume-value">${Math.round(volume)}%</span>
                    </div>
                    
                    ${isPlaying ? `
                        <div class="equalizer">
                            <div class="equalizer-bar"></div>
                            <div class="equalizer-bar"></div>
                            <div class="equalizer-bar"></div>
                            <div class="equalizer-bar"></div>
                            <div class="equalizer-bar"></div>
                        </div>
                    ` : ''}
                </div>
            </div>
        </div>
    `;
}

/**
 * Show error message
 */
function showError(message) {
    const container = document.getElementById('roomsContainer');
    container.innerHTML = `
        <div style="text-align: center; padding: 60px 20px;">
            <div style="font-size: 48px; margin-bottom: 20px;">⚠️</div>
            <h2 style="color: #EF5350; margin-bottom: 10px;">Error</h2>
            <p style="color: rgba(255,255,255,0.7);">${message}</p>
        </div>
    `;
}

/**
 * Initialize audio player for a room
 */
function initAudioPlayer(roomId, audioUrl, volume) {
    // If player already exists, update volume
    if (audioPlayers[roomId]) {
        audioPlayers[roomId].volume(volume);
        if (!audioPlayers[roomId].playing()) {
            audioPlayers[roomId].play();
        }
        return;
    }
    
    // Create new Howler instance
    audioPlayers[roomId] = new Howl({
        src: [audioUrl],
        html5: true,
        loop: true,
        volume: volume,
        autoplay: true,
        onplay: function() {
            updateMusicState(roomId, '▶️ Playing');
        },
        onpause: function() {
            updateMusicState(roomId, '⏸️ Paused');
        },
        onstop: function() {
            updateMusicState(roomId, '⏹️ Stopped');
        },
        onloaderror: function(id, error) {
            console.error(`Audio load error for ${roomId}:`, error);
            updateMusicState(roomId, '❌ Error loading audio');
        },
        onplayerror: function(id, error) {
            console.error(`Audio play error for ${roomId}:`, error);
        }
    });
    
    console.log(`🎵 Initialized audio player for ${roomId}`);
}

/**
 * Stop audio player for a room
 */
function stopAudioPlayer(roomId) {
    if (audioPlayers[roomId]) {
        audioPlayers[roomId].stop();
        audioPlayers[roomId].unload();
        delete audioPlayers[roomId];
        updateMusicState(roomId, '⏹️ Stopped');
        console.log(`⏹️ Stopped audio player for ${roomId}`);
    }
}

/**
 * Toggle play/pause for a room
 */
function toggleAudio(roomId) {
    const player = audioPlayers[roomId];
    
    if (!player) {
        // Find the room and initialize player
        const room = rooms.find(r => r.room_id === roomId);
        if (room) {
            const playlist = room.environment?.music_playlist_id || 'none';
            const playlistData = PLAYLISTS[playlist];
            if (playlistData && playlistData.url) {
                const volume = (room.environment?.music_volume || 0.3);
                initAudioPlayer(roomId, playlistData.url, volume);
            }
        }
        return;
    }
    
    if (player.playing()) {
        player.pause();
        console.log(`⏸️ Paused audio for ${roomId}`);
    } else {
        player.play();
        console.log(`▶️ Playing audio for ${roomId}`);
    }
}

/**
 * Adjust volume for a room
 */
function adjustVolume(roomId, delta) {
    const player = audioPlayers[roomId];
    if (!player) return;
    
    const currentVolume = player.volume();
    const newVolume = Math.max(0, Math.min(1, currentVolume + (delta / 100)));
    player.volume(newVolume);
    
    console.log(`🔊 Adjusted volume for ${roomId}: ${Math.round(newVolume * 100)}%`);
}

/**
 * Update music state display
 */
function updateMusicState(roomId, state) {
    const stateElement = document.getElementById(`musicState_${roomId}`);
    if (stateElement) {
        stateElement.textContent = state;
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', initSimulator);

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (refreshInterval) {
        clearInterval(refreshInterval);
    }
    
    // Stop all audio players
    Object.keys(audioPlayers).forEach(roomId => {
        stopAudioPlayer(roomId);
    });
});
