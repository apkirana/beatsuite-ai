/**
 * Gemini Live API Integration - Fixed Version
 * Real-time bidirectional voice conversation with Gemini 2.0
 * Uses WebSocket for streaming audio communication
 */

class GeminiLive {
    constructor(roomId, roomData) {
        this.roomId = roomId;
        this.roomData = roomData;
        this.isActive = false;
        this.websocket = null;
        this.mediaRecorder = null;
        this.audioContext = null;
        this.audioQueue = [];
        this.isPlaying = false;
        
        // Configuration
        this.config = {
            model: 'models/gemini-2.0-flash-exp',
            generationConfig: {
                responseModalities: "audio",
                speechConfig: {
                    voiceConfig: {
                        prebuiltVoiceConfig: {
                            voiceName: "Aoede" // Natural, empathetic voice for healthcare
                        }
                    }
                }
            },
            systemInstruction: this.getSystemInstruction()
        };
    }
    
    /**
     * Get system instruction for healthcare context
     */
    getSystemInstruction() {
        const patientName = this.roomData.patient_name || 'the patient';
        const vitals = this.roomData.vitals || {};
        
        return {
            parts: [{
                text: `You are Dr. AI, a caring medical AI assistant at Beat Suite AI healthcare system. 
You're helping with ${patientName}'s care in ${this.roomId}.

Current Vitals:
- Heart Rate: ${vitals.heart_rate || 'N/A'} BPM
- Temperature: ${vitals.temperature || 'N/A'}°F
- SpO2: ${vitals.spo2 || 'N/A'}%
- Movement Level: ${vitals.movement_level || 'N/A'}

You provide empathetic, professional healthcare guidance. Keep responses conversational but medically accurate. 
Ask relevant questions about symptoms, comfort, and wellbeing. Always prioritize patient safety.

Current room environment:
- Light: ${this.roomData.light_brightness || 50}% brightness, ${this.roomData.light_color || 'neutral'} tone
- Music: ${this.roomData.music_volume || 30}% volume, ${this.roomData.music_type || 'ambient'} style
- Temperature: ${this.roomData.room_temperature || 72}°F

You can suggest environment adjustments for comfort and healing.`
            }]
        };
    }

    /**
     * Start Gemini Live session
     */
    async start() {
        try {
            console.log('🚀 Starting Gemini Live session for room:', this.roomId);
            this.updateUI('connecting', 'Connecting...');
            
            // Get API key from backend
            console.log('📡 Fetching API token from backend...');
            const response = await fetch('/api/ai/live/token', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ room_id: this.roomId })
            });
            
            console.log('📥 Token response status:', response.status);
            
            if (!response.ok) {
                const errorText = await response.text();
                console.error('❌ Token request failed:', errorText);
                throw new Error(`Failed to get API token: ${response.status} ${errorText}`);
            }
            
            const data = await response.json();
            console.log('✅ Got token response:', { success: data.success, hasToken: !!data.token });
            
            if (!data.success || !data.token) {
                throw new Error(data.message || 'No API token received');
            }
            
            const apiKey = data.token;
            
            // Initialize WebSocket connection to Gemini Live API
            // Updated endpoint for Gemini 2.0 Live API
            const wsUrl = `wss://generativelanguage.googleapis.com/ws/google.ai.generativelanguage.v1alpha.GenerativeService.BidiGenerateContent?key=${apiKey}`;
            console.log('🔌 Connecting to Gemini Live WebSocket...');
            
            this.websocket = new WebSocket(wsUrl);
            
            // Set up connection timeout
            const connectionTimeout = setTimeout(() => {
                if (this.websocket.readyState === WebSocket.CONNECTING) {
                    console.error('❌ WebSocket connection timeout');
                    this.websocket.close();
                    this.updateUI('error', 'Connection timeout - please try again');
                }
            }, 10000); // 10 second timeout
            
            this.websocket.onopen = () => {
                console.log('✅ WebSocket connected to Gemini Live');
                clearTimeout(connectionTimeout);
                this.sendSetup();
            };
            
            this.websocket.onmessage = (event) => {
                this.handleServerMessage(event.data);
            };
            
            this.websocket.onerror = (error) => {
                console.error('❌ WebSocket error:', error);
                clearTimeout(connectionTimeout);
                this.updateUI('error', 'Connection error - check your internet connection');
            };
            
            this.websocket.onclose = (event) => {
                console.log('🔌 WebSocket closed:', event.code, event.reason);
                clearTimeout(connectionTimeout);
                if (this.isActive) {
                    // Unexpected close
                    this.updateUI('error', 'Connection lost');
                }
                this.stop();
            };
            
        } catch (error) {
            console.error('❌ Failed to start Gemini Live:', error);
            this.updateUI('error', error.message);
        }
    }
    
    /**
     * Send setup configuration to Gemini
     */
    sendSetup() {
        const setupMessage = {
            setup: this.config
        };
        
        console.log('📤 Sending setup configuration...');
        this.websocket.send(JSON.stringify(setupMessage));
    }
    
    /**
     * Start capturing audio from microphone
     */
    async startAudioCapture() {
        try {
            // Check for browser compatibility
            if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
                throw new Error('Microphone access not supported by this browser');
            }

            console.log('🎤 Requesting microphone access...');
            const stream = await navigator.mediaDevices.getUserMedia({ 
                audio: {
                    channelCount: 1,
                    sampleRate: 16000,
                    echoCancellation: true,
                    noiseSuppression: true,
                    autoGainControl: true
                } 
            });
            
            console.log('✅ Microphone access granted');
            
            // Create AudioContext for processing
            this.audioContext = new (window.AudioContext || window.webkitAudioContext)({
                sampleRate: 16000
            });
            
            // Resume audio context if suspended (Safari/iOS requirement)
            if (this.audioContext.state === 'suspended') {
                await this.audioContext.resume();
            }
            
            // Use compatible MIME types
            let mimeType = 'audio/webm;codecs=opus';
            if (!MediaRecorder.isTypeSupported(mimeType)) {
                mimeType = 'audio/webm';
                if (!MediaRecorder.isTypeSupported(mimeType)) {
                    mimeType = 'audio/mp4';
                    if (!MediaRecorder.isTypeSupported(mimeType)) {
                        mimeType = ''; // Let browser choose
                    }
                }
            }
            
            console.log('🎵 Using MIME type:', mimeType || 'browser default');
            
            // Create MediaRecorder with compatible format
            this.mediaRecorder = new MediaRecorder(stream, {
                mimeType: mimeType || undefined,
                audioBitsPerSecond: 64000 // Higher quality for better recognition
            });
            
            this.mediaRecorder.ondataavailable = (event) => {
                if (event.data.size > 0 && this.websocket?.readyState === WebSocket.OPEN) {
                    // Convert to base64 and send to Gemini
                    const reader = new FileReader();
                    reader.onloadend = () => {
                        const base64Audio = reader.result.split(',')[1];
                        this.sendAudioData(base64Audio, mimeType || 'audio/webm');
                    };
                    reader.readAsDataURL(event.data);
                }
            };
            
            this.mediaRecorder.onerror = (error) => {
                console.error('❌ MediaRecorder error:', error);
                this.updateUI('error', 'Audio recording error');
            };
            
            // Send audio chunks every 500ms for better stability
            this.mediaRecorder.start(500);
            console.log('▶️ Audio streaming started');
            
        } catch (error) {
            console.error('❌ Microphone access denied:', error);
            this.updateUI('error', 'Microphone access required. Please allow microphone access and try again.');
        }
    }

    /**
     * Send audio data to Gemini
     */
    sendAudioData(base64Audio, mimeType = 'audio/webm') {
        try {
            const message = {
                realtimeInput: {
                    mediaChunks: [{
                        mimeType: mimeType,
                        data: base64Audio
                    }]
                }
            };
            
            if (this.websocket?.readyState === WebSocket.OPEN) {
                this.websocket.send(JSON.stringify(message));
            }
        } catch (error) {
            console.error('❌ Error sending audio data:', error);
        }
    }

    /**
     * Handle messages from Gemini server
     */
    async handleServerMessage(data) {
        try {
            const message = JSON.parse(data);
            console.log('📥 Received message from Gemini:', message);
            
            // Handle setup completion
            if (message.setupComplete) {
                console.log('✅ Gemini setup complete - starting audio capture...');
                await this.startAudioCapture();
                this.isActive = true;
                this.updateUI('listening', 'Listening... speak naturally');
                return;
            }
            
            // Handle server content (audio responses)
            if (message.serverContent) {
                const parts = message.serverContent.modelTurn?.parts || [];
                
                for (const part of parts) {
                    // Handle audio response
                    if (part.inlineData?.mimeType?.startsWith('audio/')) {
                        console.log('🔊 Received audio response from Gemini');
                        const audioData = part.inlineData.data;
                        await this.playAudio(audioData);
                    }
                    
                    // Handle text response (for display)
                    if (part.text) {
                        console.log('💬 Received text response:', part.text);
                        this.displayTranscript('AI', part.text);
                    }
                }
                
                // Show turn complete
                if (message.serverContent.turnComplete) {
                    console.log('✅ AI finished speaking');
                    this.updateUI('listening', 'Your turn - speak now');
                }
            }
            
            // Handle tool call responses
            if (message.toolCallCancellation) {
                console.log('🔧 Tool call cancelled');
            }
            
            // Handle tool calls (if needed for future features)
            if (message.toolCall) {
                console.log('🔧 Tool call:', message.toolCall);
            }
            
            // Handle errors
            if (message.error) {
                console.error('❌ Server error:', message.error);
                this.updateUI('error', `Server error: ${message.error.message || 'Unknown error'}`);
            }
            
        } catch (error) {
            console.error('❌ Error handling server message:', error);
            this.updateUI('error', 'Error processing server response');
        }
    }

    /**
     * Play audio response from Gemini
     */
    async playAudio(base64Audio) {
        try {
            // Decode base64 to ArrayBuffer
            const binaryString = atob(base64Audio);
            const bytes = new Uint8Array(binaryString.length);
            for (let i = 0; i < binaryString.length; i++) {
                bytes[i] = binaryString.charCodeAt(i);
            }
            
            // Create audio context if needed
            if (!this.audioContext) {
                this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
            }
            
            // Resume if suspended
            if (this.audioContext.state === 'suspended') {
                await this.audioContext.resume();
            }
            
            // Decode and play audio
            const audioBuffer = await this.audioContext.decodeAudioData(bytes.buffer);
            const source = this.audioContext.createBufferSource();
            source.buffer = audioBuffer;
            source.connect(this.audioContext.destination);
            
            this.updateUI('speaking', 'AI is speaking...');
            
            source.onended = () => {
                this.updateUI('listening', 'Listening...');
            };
            
            source.start(0);
            
        } catch (error) {
            console.error('❌ Error playing audio:', error);
            this.updateUI('error', 'Audio playback error');
        }
    }
    
    /**
     * Display conversation transcript
     * This method can be overridden by the dashboard to use specific elements
     */
    displayTranscript(speaker, text) {
        const transcriptEl = document.getElementById(`gemini-live-transcript-${this.roomId}`);
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
    }
    
    /**
     * Update UI status
     * This method can be overridden by the dashboard to use specific elements
     */
    updateUI(state, message = '') {
        const statusEl = document.getElementById(`gemini-live-status-${this.roomId}`);
        const buttonEl = document.getElementById(`gemini-live-toggle-${this.roomId}`);
        
        if (statusEl) {
            let icon = '⚪';
            let color = '#666';
            
            switch (state) {
                case 'connecting':
                    icon = '🔄';
                    color = '#f59e0b';
                    message = message || 'Connecting...';
                    break;
                case 'active':
                    icon = '🟢';
                    color = '#10b981';
                    message = message || 'Connected - Initializing...';
                    break;
                case 'listening':
                    icon = '🎤';
                    color = '#3b82f6';
                    message = message || 'Listening...';
                    break;
                case 'speaking':
                    icon = '🔊';
                    color = '#8b5cf6';
                    message = message || 'Speaking...';
                    break;
                case 'error':
                    icon = '❌';
                    color = '#ef4444';
                    message = message || 'Error';
                    break;
                default:
                    icon = '⚪';
                    color = '#666';
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
        const transcriptEl = document.getElementById(`gemini-live-transcript-${this.roomId}`);
        if (transcriptEl && this.isActive) {
            transcriptEl.style.display = 'block';
        } else if (transcriptEl) {
            transcriptEl.style.display = 'none';
        }
    }

    /**
     * Stop Gemini Live session
     */
    stop() {
        console.log('🛑 Stopping Gemini Live session...');
        
        this.isActive = false;
        
        // Stop media recorder
        if (this.mediaRecorder && this.mediaRecorder.state !== 'inactive') {
            this.mediaRecorder.stop();
            if (this.mediaRecorder.stream) {
                this.mediaRecorder.stream.getTracks().forEach(track => track.stop());
            }
        }
        
        // Close WebSocket
        if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
            this.websocket.close();
        }
        
        // Close audio context
        if (this.audioContext) {
            this.audioContext.close().catch(console.warn);
        }
        
        this.updateUI('inactive', 'Disconnected');
        console.log('✅ Gemini Live session stopped');
    }
    
    /**
     * Toggle Gemini Live on/off
     */
    toggle() {
        console.log('🔄 Toggle called, current state:', this.isActive);
        if (this.isActive) {
            this.stop();
        } else {
            this.start();
        }
    }
}

// Export for use in other modules
console.log('✅ GeminiLive class loaded and ready');
window.GeminiLive = GeminiLive;