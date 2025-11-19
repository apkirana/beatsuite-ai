/**
 * Gemini Live API Integration
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
- Blood Pressure: ${vitals.blood_pressure || 'N/A'}

Patient Status: ${this.roomData.patient_status || 'Monitoring'}
AI Control: ${this.roomData.ai_control_active ? 'Active' : 'Manual'}

Your communication style:
- Speak naturally and warmly, like a caring nurse
- Use conversational language, contractions (I'm, they're, etc.)
- Be reassuring when vitals are good
- Show concern and urgency when needed
- Keep responses concise - 1-3 sentences typically
- Sound human, not robotic

You can discuss:
- Patient vital signs and their meaning
- Current health status and comfort
- Sleep stages and rest quality
- Pain indicators and comfort measures
- Room environment (lights, music, temperature)
- General care recommendations

Always prioritize patient comfort and clear communication with healthcare staff and family.`
            }]
        };
    }
    
    /**
     * Initialize and start Gemini Live session
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
            const wsUrl = `wss://generativelanguage.googleapis.com/ws/google.ai.generativelanguage.v1alpha.GenerativeService.BidiGenerateContent?key=${apiKey}`;
            console.log('🔌 Connecting to Gemini Live WebSocket...');
            
            this.websocket = new WebSocket(wsUrl);
            
            this.websocket.onopen = () => {
                console.log('✅ WebSocket connected to Gemini Live');
                this.sendSetup();
                this.startAudioCapture();
                this.isActive = true;
                this.updateUI('active');
            };
            
            this.websocket.onmessage = (event) => {
                this.handleServerMessage(event.data);
            };
            
            this.websocket.onerror = (error) => {
                console.error('❌ WebSocket error:', error);
                this.updateUI('error', 'Connection error');
            };
            
            this.websocket.onclose = () => {
                console.log('🔌 WebSocket closed');
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
            const stream = await navigator.mediaDevices.getUserMedia({ 
                audio: {
                    channelCount: 1,
                    sampleRate: 16000,
                    echoCancellation: true,
                    noiseSuppression: true
                } 
            });
            
            console.log('🎤 Microphone access granted');
            
            // Create AudioContext for processing
            this.audioContext = new (window.AudioContext || window.webkitAudioContext)({
                sampleRate: 16000
            });
            
            // Create MediaRecorder for PCM16 audio
            this.mediaRecorder = new MediaRecorder(stream, {
                mimeType: 'audio/webm;codecs=pcm',
                audioBitsPerSecond: 16000
            });
            
            this.mediaRecorder.ondataavailable = (event) => {
                if (event.data.size > 0 && this.websocket?.readyState === WebSocket.OPEN) {
                    // Convert to base64 and send to Gemini
                    const reader = new FileReader();
                    reader.onloadend = () => {
                        const base64Audio = reader.result.split(',')[1];
                        this.sendAudioData(base64Audio);
                    };
                    reader.readAsDataURL(event.data);
                }
            };
            
            // Send audio chunks every 100ms
            this.mediaRecorder.start(100);
            console.log('▶️ Audio streaming started');
            
        } catch (error) {
            console.error('❌ Microphone access denied:', error);
            this.updateUI('error', 'Microphone access required');
        }
    }
    
    /**
     * Send audio data to Gemini
     */
    sendAudioData(base64Audio) {
        const message = {
            realtimeInput: {
                mediaChunks: [{
                    mimeType: "audio/pcm;rate=16000",
                    data: base64Audio
                }]
            }
        };
        
        this.websocket.send(JSON.stringify(message));
    }
    
    /**
     * Handle messages from Gemini server
     */
    async handleServerMessage(data) {
        try {
            const message = JSON.parse(data);
            
            // Handle setup completion
            if (message.setupComplete) {
                console.log('✅ Setup complete');
                this.updateUI('listening', 'Listening... speak naturally');
            }
            
            // Handle server content (audio responses)
            if (message.serverContent) {
                const parts = message.serverContent.modelTurn?.parts || [];
                
                for (const part of parts) {
                    // Handle audio response
                    if (part.inlineData?.mimeType?.startsWith('audio/')) {
                        const audioData = part.inlineData.data;
                        await this.playAudio(audioData);
                    }
                    
                    // Handle text response (for display)
                    if (part.text) {
                        this.displayTranscript('AI', part.text);
                    }
                }
                
                // Show turn complete
                if (message.serverContent.turnComplete) {
                    console.log('✅ AI finished speaking');
                    this.updateUI('listening', 'Your turn - speak now');
                }
            }
            
            // Handle tool calls (if needed for future features)
            if (message.toolCall) {
                console.log('🔧 Tool call:', message.toolCall);
            }
            
        } catch (error) {
            console.error('❌ Error handling server message:', error);
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
            messageEl.className = `transcript-message ${speaker.toLowerCase()}`;
            messageEl.innerHTML = `
                <span class="speaker">${speaker}:</span>
                <span class="text">${text}</span>
            `;
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
                    break;
                case 'speaking':
                    icon = '🔊';
                    color = '#8b5cf6';
                    break;
                case 'error':
                    icon = '❌';
                    color = '#ef4444';
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
                buttonEl.textContent = 'Stop Live Chat';
                buttonEl.classList.add('active');
            } else {
                buttonEl.textContent = 'Start Live Chat';
                buttonEl.classList.remove('active');
            }
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
            this.mediaRecorder.stream.getTracks().forEach(track => track.stop());
        }
        
        // Close WebSocket
        if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
            this.websocket.close();
        }
        
        // Close audio context
        if (this.audioContext) {
            this.audioContext.close();
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
console.log('✅ GeminiLive class loaded');
window.GeminiLive = GeminiLive;
