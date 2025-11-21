/**
 * Quick Voice Assistant - Simplified, reliable voice chat
 * One-click voice interaction with better error handling
 */

class QuickVoiceAssistant {
    constructor(roomId, roomData) {
        this.roomId = roomId;
        this.roomData = roomData;
        this.isListening = false;
        this.isSpeaking = false;
        this.recognition = null;
        this.synthesis = window.speechSynthesis;
        
        this.initializeSpeechRecognition();
    }
    
    initializeSpeechRecognition() {
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            this.recognition = new SpeechRecognition();
            
            // Configure speech recognition
            this.recognition.continuous = false;  // One shot recognition
            this.recognition.interimResults = false;
            this.recognition.lang = 'en-US';
            this.recognition.maxAlternatives = 1;
            
            // Handle speech recognition events
            this.recognition.onstart = () => {
                console.log('🎤 Voice recognition started');
                this.updateStatus('🎤 Listening... speak now!');
                this.isListening = true;
                this.updateButton();
            };
            
            this.recognition.onresult = (event) => {
                const transcript = event.results[0][0].transcript;
                console.log('🗣️ Voice recognized:', transcript);
                this.handleVoiceInput(transcript);
            };
            
            this.recognition.onerror = (event) => {
                console.error('❌ Speech recognition error:', event.error);
                this.isListening = false;
                this.updateButton();
                
                if (event.error === 'not-allowed') {
                    this.updateStatus('❌ Microphone access denied. Please allow microphone permissions.');
                } else if (event.error === 'no-speech') {
                    this.updateStatus('⚠️ No speech detected. Try again.');
                } else {
                    this.updateStatus('❌ Voice recognition error. Please try again.');
                }
            };
            
            this.recognition.onend = () => {
                console.log('🛑 Voice recognition ended');
                this.isListening = false;
                this.updateButton();
            };
        }
    }
    
    /**
     * One-click voice interaction
     */
    async startQuickVoice() {
        if (!this.recognition) {
            alert('Speech recognition not supported. Please use Chrome, Edge, or Safari.');
            return;
        }
        
        if (this.isListening) {
            this.stopListening();
            return;
        }
        
        try {
            this.updateStatus('🎤 Starting microphone...');
            this.recognition.start();
        } catch (error) {
            console.error('Failed to start recognition:', error);
            this.updateStatus('❌ Failed to start microphone. Try again.');
            this.isListening = false;
            this.updateButton();
        }
    }
    
    stopListening() {
        if (this.recognition && this.isListening) {
            this.recognition.stop();
            this.updateStatus('🛑 Stopped listening');
        }
    }
    
    /**
     * Handle voice input and get AI response
     */
    async handleVoiceInput(transcript) {
        this.updateStatus('🤔 Processing your request...');
        this.addMessageToChat('user', transcript);
        
        try {
            // Send to AI assistant API
            const response = await this.getAIResponse(transcript);
            
            if (response.success) {
                this.addMessageToChat('assistant', response.message);
                this.speakResponse(response.message);
                this.updateStatus('✅ Ready for next question');
            } else {
                throw new Error(response.error || 'Failed to get AI response');
            }
        } catch (error) {
            console.error('AI response error:', error);
            const errorMsg = 'Sorry, I had trouble processing your request. Please try again.';
            this.addMessageToChat('assistant', errorMsg);
            this.updateStatus('⚠️ Error - Ready to try again');
        }
    }
    
    /**
     * Get AI response from backend
     */
    async getAIResponse(query) {
        try {
            const response = await fetch('/api/assistant/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${window.authUtils.getToken()}`
                },
                body: JSON.stringify({
                    room_id: this.roomId,
                    message: query,
                    context: {
                        patient_name: this.roomData.patient_name,
                        room_data: this.roomData
                    }
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            return {
                success: true,
                message: data.response || data.message || 'I understand your request.'
            };
        } catch (error) {
            console.error('API request failed:', error);
            return {
                success: false,
                error: error.message
            };
        }
    }
    
    /**
     * Speak AI response
     */
    speakResponse(text) {
        if (!text || this.isSpeaking) return;
        
        console.log('🔊 Attempting to speak:', text);
        
        // Ensure voices are loaded
        this.ensureVoicesLoaded(() => {
            this.performSpeech(text);
        });
    }
    
    /**
     * Ensure voices are loaded before speaking
     */
    ensureVoicesLoaded(callback) {
        const voices = this.synthesis.getVoices();
        
        if (voices.length > 0) {
            callback();
            return;
        }
        
        console.log('🔄 Loading voices...');
        
        // Wait for voices to load
        const checkVoices = () => {
            const voices = this.synthesis.getVoices();
            if (voices.length > 0) {
                console.log('✅ Voices loaded:', voices.length);
                callback();
            } else {
                setTimeout(checkVoices, 100);
            }
        };
        
        if ('onvoiceschanged' in this.synthesis) {
            this.synthesis.onvoiceschanged = () => {
                console.log('🔄 Voices changed event');
                checkVoices();
            };
        }
        
        // Fallback timeout
        setTimeout(() => {
            console.log('⏰ Voice loading timeout - proceeding anyway');
            callback();
        }, 2000);
        
        checkVoices();
    }
    
    /**
     * Perform the actual speech synthesis
     */
    performSpeech(text) {
        try {
            // Stop any current speech
            this.synthesis.cancel();
            
            // Create speech utterance
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.rate = 0.8;  // Slower for clarity
            utterance.pitch = 1.0;
            utterance.volume = 1.0;  // Max volume
            
            // Find the best voice
            const voices = this.synthesis.getVoices();
            console.log('📢 Available voices:', voices.length);
            
            let selectedVoice = null;
            
            // Priority 1: Female English voices
            selectedVoice = voices.find(voice => 
                voice.lang.startsWith('en') && 
                (voice.name.includes('Female') || voice.name.includes('Samantha') || 
                 voice.name.includes('Karen') || voice.name.includes('Susan'))
            );
            
            // Priority 2: Any Google English voice
            if (!selectedVoice) {
                selectedVoice = voices.find(voice => 
                    voice.lang.startsWith('en') && voice.name.includes('Google')
                );
            }
            
            // Priority 3: Any English voice
            if (!selectedVoice) {
                selectedVoice = voices.find(voice => voice.lang.startsWith('en'));
            }
            
            // Priority 4: Default system voice
            if (!selectedVoice && voices.length > 0) {
                selectedVoice = voices[0];
            }
            
            if (selectedVoice) {
                utterance.voice = selectedVoice;
                console.log('🗣️ Selected voice:', selectedVoice.name, selectedVoice.lang);
            } else {
                console.log('⚠️ No specific voice selected, using default');
            }
            
            // Event handlers
            utterance.onstart = () => {
                console.log('🔊 Speech started');
                this.isSpeaking = true;
                this.updateStatus('🔊 Speaking...');
            };
            
            utterance.onend = () => {
                console.log('✅ Speech completed');
                this.isSpeaking = false;
                this.updateStatus('✅ Ready for next question');
            };
            
            utterance.onerror = (event) => {
                console.error('❌ Speech synthesis error:', event);
                this.isSpeaking = false;
                this.updateStatus('⚠️ Voice error - Ready to continue');
                
                // Show user-friendly message
                this.addMessageToChat('assistant', `[Voice Error: ${event.error}. Text response shown instead.]`);
            };
            
            // Start speaking
            console.log('🎵 Starting speech synthesis...');
            this.synthesis.speak(utterance);
            
            // Fallback timeout
            setTimeout(() => {
                if (this.isSpeaking) {
                    console.log('⏰ Speech timeout - stopping');
                    this.synthesis.cancel();
                    this.isSpeaking = false;
                    this.updateStatus('⚠️ Speech timeout - Ready to continue');
                }
            }, 30000); // 30 second timeout
            
        } catch (error) {
            console.error('❌ Speech synthesis failed:', error);
            this.isSpeaking = false;
            this.updateStatus('⚠️ Voice unavailable - Ready to continue');
            this.addMessageToChat('assistant', '[Voice synthesis failed - text response only]');
        }
    }
    
    /**
     * Add message to chat interface
     */
    addMessageToChat(role, message) {
        const chatContainer = document.getElementById(`chat-messages-${this.roomId}`);
        if (!chatContainer) return;
        
        const messageDiv = document.createElement('div');
        messageDiv.className = `assistant-message ${role}`;
        
        const timestamp = new Date().toLocaleTimeString();
        const avatar = role === 'user' ? '👤' : '🤖';
        
        messageDiv.innerHTML = `
            <div style="display: flex; gap: 12px; margin-bottom: 16px;">
                <div style="flex-shrink: 0; width: 36px; height: 36px; border-radius: 50%; background: ${role === 'user' ? '#E3F2FD' : '#F3E5F5'}; display: flex; align-items: center; justify-content: center; font-size: 18px;">
                    ${avatar}
                </div>
                <div style="flex: 1;">
                    <div style="font-weight: 600; font-size: 13px; color: #666; margin-bottom: 4px;">
                        ${role === 'user' ? 'You' : 'AI Assistant'} • ${timestamp}
                    </div>
                    <div style="color: #333; line-height: 1.5; font-size: 14px;">
                        ${message}
                    </div>
                </div>
            </div>
        `;
        
        chatContainer.appendChild(messageDiv);
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }
    
    /**
     * Update status display
     */
    updateStatus(status) {
        const statusElement = document.getElementById(`quick-voice-status-${this.roomId}`);
        if (statusElement) {
            statusElement.textContent = status;
        }
    }
    
    /**
     * Update button state
     */
    updateButton() {
        const button = document.getElementById(`quick-voice-btn-${this.roomId}`);
        if (!button) return;
        
        if (this.isListening) {
            button.style.background = 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)';
            button.innerHTML = `
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                    <rect x="6" y="6" width="12" height="12"></rect>
                </svg>
                <span>Stop Listening</span>
            `;
        } else {
            button.style.background = 'linear-gradient(135deg, #10b981 0%, #059669 100%)';
            button.innerHTML = `
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                    <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path>
                    <path d="M19 10v2a7 7 0 0 1-14 0v-2"></path>
                    <line x1="12" y1="19" x2="12" y2="23"></line>
                    <line x1="8" y1="23" x2="16" y2="23"></line>
                </svg>
                <span>Quick Voice Chat</span>
            `;
        }
    }
}

// Global instances
window.quickVoiceAssistants = window.quickVoiceAssistants || {};

/**
 * Initialize quick voice assistant for a room
 */
function initQuickVoiceAssistant(roomId, roomData) {
    if (!window.quickVoiceAssistants[roomId]) {
        window.quickVoiceAssistants[roomId] = new QuickVoiceAssistant(roomId, roomData);
    }
}

/**
 * Start quick voice for a room
 */
function startQuickVoice(roomId) {
    const assistant = window.quickVoiceAssistants[roomId];
    if (assistant) {
        assistant.startQuickVoice();
    } else {
        console.error('Quick voice assistant not initialized for room:', roomId);
    }
}