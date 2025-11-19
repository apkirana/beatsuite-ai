/**
 * Smart Assistant - Voice & Text AI Chatbot
 * Personalized AI assistant for each patient room
 */

class SmartAssistant {
    constructor(roomId, roomData) {
        this.roomId = roomId;
        this.roomData = roomData;
        this.isListening = false;
        this.isSpeaking = false;
        this.isMuted = false;
        this.recognition = null;
        this.synthesis = window.speechSynthesis;
        this.conversationHistory = []; // Store conversation for context
        
        // Initialize Speech Recognition if available
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            this.recognition = new SpeechRecognition();
            this.recognition.continuous = true;  // Keep listening for multiple queries
            this.recognition.interimResults = true;  // Show interim results
            this.recognition.lang = 'en-US';
            this.recognition.maxAlternatives = 1;
            
            this.recognition.onresult = (event) => {
                const last = event.results.length - 1;
                const transcript = event.results[last][0].transcript;
                const isFinal = event.results[last].isFinal;
                
                if (isFinal) {
                    console.log('🎤 Voice recognized:', transcript);
                    this.handleUserQuery(transcript);
                    // Keep listening for next question
                    this.updateAssistantStatus('🎤 Listening for next question...');
                } else {
                    // Show interim results
                    console.log('🎤 Interim:', transcript);
                }
            };
            
            this.recognition.onerror = (event) => {
                console.error('❌ Speech recognition error:', event.error);
                if (event.error === 'no-speech') {
                    this.updateAssistantStatus('🎤 No speech detected, still listening...');
                    // Don't stop, keep listening
                } else if (event.error === 'aborted') {
                    this.updateAssistantStatus('Ready');
                    this.isListening = false;
                    this.updateMicButton();
                } else {
                    this.updateAssistantStatus('⚠️ Error: ' + event.error);
                    this.isListening = false;
                    this.updateMicButton();
                }
            };
            
            this.recognition.onend = () => {
                // Auto-restart if still in listening mode
                if (this.isListening) {
                    console.log('🔄 Restarting speech recognition...');
                    try {
                        this.recognition.start();
                    } catch (e) {
                        console.log('⚠️ Could not restart recognition:', e);
                        this.isListening = false;
                        this.updateMicButton();
                        this.updateAssistantStatus('Ready');
                    }
                } else {
                    this.updateMicButton();
                    this.updateAssistantStatus('Ready');
                }
            };
        }
    }
    
    /**
     * Toggle voice input
     */
    toggleVoiceInput() {
        if (!this.recognition) {
            alert('Speech recognition is not supported in your browser. Please use Chrome or Edge.');
            return;
        }
        
        if (this.isListening) {
            // Stop listening
            console.log('🛑 Stopping voice input');
            this.isListening = false;
            try {
                this.recognition.stop();
            } catch (e) {
                console.log('⚠️ Recognition already stopped');
            }
            this.updateAssistantStatus('Ready - Tap mic to speak');
            this.updateMicButton();
        } else {
            // Start listening
            console.log('▶️ Starting voice input (continuous mode)');
            this.isListening = true;
            
            try {
                this.updateAssistantStatus('🎤 Starting microphone... (allow permission if asked)');
                this.recognition.start();
                
                // Update status after recognition actually starts
                setTimeout(() => {
                    if (this.isListening) {
                        this.updateAssistantStatus('🎤 Listening... (speak your questions)');
                    }
                }, 500);
                
                this.updateMicButton();
            } catch (e) {
                console.error('❌ Failed to start recognition:', e);
                this.isListening = false;
                this.updateMicButton();
                this.updateAssistantStatus('❌ Microphone access denied or unavailable');
                
                // Show helpful message
                setTimeout(() => {
                    this.updateAssistantStatus('Ready - Tap mic to try again');
                }, 3000);
            }
        }
    }
    
    /**
     * Handle user query (text or voice)
     */
    async handleUserQuery(query) {
        if (!query || query.trim() === '') return;
        
        // Add to conversation history
        this.conversationHistory.push({
            role: 'user',
            content: query,
            timestamp: new Date().toISOString()
        });
        
        // Add user message to chat
        this.addMessageToChat('user', query);
        
        this.updateAssistantStatus('🤔 Thinking...');
        
        // Generate AI response with conversation history
        const response = await this.generateAIResponse(query);
        
        // Add to conversation history
        this.conversationHistory.push({
            role: 'assistant',
            content: response,
            timestamp: new Date().toISOString()
        });
        
        // Add AI response to chat
        this.addMessageToChat('assistant', response);
        
        // Speak the response
        this.speak(response);
        
        // Restore listening status or set to ready
        if (this.isListening) {
            this.updateAssistantStatus('🎤 Listening for next question...');
        } else {
            this.updateAssistantStatus('Ready');
        }
        
        console.log('💬 Conversation history:', this.conversationHistory.length, 'messages');
    }    /**
     * Generate AI response using backend API with conversation history
     */
    async generateAIResponse(query) {
        const context = this.buildContext();
        
        // Add conversation history to context (last 5 exchanges for context)
        const recentHistory = this.conversationHistory.slice(-10);
        
        console.log('🤖 Sending query to AI:', query);
        console.log('📊 Context:', context);
        console.log('💬 History:', recentHistory.length, 'messages');
        
        try {
            const response = await fetch('/api/assistant/query', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'include',
                body: JSON.stringify({
                    room_id: this.roomId,
                    query: query,
                    context: context,
                    conversation_history: recentHistory
                })
            });
            
            if (!response.ok) {
                console.error('❌ AI API response not OK:', response.status, response.statusText);
                throw new Error('Failed to get AI response');
            }
            
            const data = await response.json();
            console.log('✅ AI Response received:', data.response.substring(0, 100) + '...');
            return data.response;
        } catch (error) {
            console.error('❌ AI API error:', error);
            console.log('📱 Using local fallback response');
            // Fallback to local context-based response
            return this.generateLocalResponse(query);
        }
    }
    
    /**
     * Build context for AI
     */
    buildContext() {
        const room = this.roomData;
        return {
            patient_name: room.patient_name,
            room_number: room.room_number,
            vitals: {
                heart_rate: room.vitals.heart_rate,
                temperature: room.vitals.temperature,
                respiratory_rate: room.vitals.respiratory_rate,
                spo2: room.vitals.spo2
            },
            sleep_stage: room.current_state.sleep_stage,
            pain_detected: room.current_state.pain_detected,
            ai_active: room.ai_control_active,
            environment: room.environment
        };
    }
    
    /**
     * Generate local fallback response
     */
    generateLocalResponse(query) {
        const room = this.roomData;
        const queryLower = query.toLowerCase();
        
        // Patient status
        if (queryLower.includes('how') && (queryLower.includes('patient') || queryLower.includes('doing'))) {
            const hr = room.vitals.heart_rate;
            const temp = room.vitals.temperature;
            const spo2 = room.vitals.spo2;
            
            let status = 'stable';
            if (room.current_state.pain_detected) status = 'experiencing some discomfort';
            else if (hr > 100 || spo2 < 95) status = 'needs attention';
            
            return `${room.patient_name} is currently ${status}. Heart rate is ${hr} BPM, temperature is ${((temp - 32) * 5/9).toFixed(1)}°C, and oxygen saturation is ${spo2}%. The patient is in ${room.current_state.sleep_stage} stage.`;
        }
        
        // Vitals
        if (queryLower.includes('vital') || queryLower.includes('heart') || queryLower.includes('temperature')) {
            return `Current vitals for ${room.patient_name}: Heart rate ${room.vitals.heart_rate} BPM, Temperature ${((room.vitals.temperature - 32) * 5/9).toFixed(1)}°C, Respiratory rate ${room.vitals.respiratory_rate}/min, SpO2 ${room.vitals.spo2}%.`;
        }
        
        // Sleep
        if (queryLower.includes('sleep') || queryLower.includes('sleeping')) {
            return `${room.patient_name} is currently in ${room.current_state.sleep_stage} stage. ${room.ai_control_active ? 'The AI is adjusting the environment to optimize sleep quality.' : 'Manual control is active.'}`;
        }
        
        // Pain
        if (queryLower.includes('pain') || queryLower.includes('discomfort')) {
            if (room.current_state.pain_detected) {
                return `Yes, pain indicators have been detected for ${room.patient_name}. The AI is adjusting the environment to help with comfort, and medical staff have been notified.`;
            } else {
                return `No pain indicators detected at the moment for ${room.patient_name}.`;
            }
        }
        
        // AI control
        if (queryLower.includes('ai') || queryLower.includes('control')) {
            if (room.ai_control_active) {
                return `AI control is active for this room. The AI is monitoring ${room.patient_name}'s condition and automatically adjusting lighting and music based on their sleep stage and comfort levels.`;
            } else {
                return `AI control is currently disabled. Staff have manual control over the room environment.`;
            }
        }
        
        // Environment
        if (queryLower.includes('light') || queryLower.includes('music') || queryLower.includes('environment')) {
            const env = room.environment;
            return `The room environment is set to: Light color ${env.light_hex_color} at ${Math.round(env.light_brightness * 100)}% brightness, and ${env.music_playlist_id ? 'playing ' + env.music_playlist_id.replace('_', ' ') + ' music' : 'no music playing'} at ${Math.round(env.music_volume * 100)}% volume.`;
        }
        
        // Default response
        return `I'm the AI assistant for ${room.patient_name} in ${room.room_number}. I can tell you about vital signs, sleep status, pain indicators, AI control status, and room environment. What would you like to know?`;
    }
    
    /**
     * Text-to-speech with natural, human-like voice (Samantha Enhanced)
     */
    speak(text) {
        if (!this.synthesis || this.isMuted) return;
        
        // Cancel any ongoing speech
        this.synthesis.cancel();
        
        const utterance = new SpeechSynthesisUtterance(text);
        
        // Optimized settings for Samantha (Enhanced) - most human-like voice
        utterance.rate = 0.95;      // Slightly slower for natural clarity
        utterance.pitch = 1.50;     // Natural, warm, conversational pitch
        utterance.volume = 1.0;     // Full, confident volume
        
        // Select the most natural, human-like voice available
        const voices = this.synthesis.getVoices();
        
        // Prioritize Samantha (Enhanced) - the most natural macOS voice
        const preferredVoices = [
            'Samantha (Enhanced)',  // Best - Premium macOS voice, extremely natural
            'Samantha',             // Good fallback
            'Ava (Premium)',        // Alternative premium option
            'Ava',
            'Allison (Premium)',
            'Allison',
            'Susan (Premium)',
            'Susan',
            'Nicky',
            // Google voices (good quality)
            'Google US English',
            'Google UK English Female',
            // Microsoft voices
            'Microsoft Aria',
            'Microsoft Zira',
            // Other quality voices
            'Karen',
            'Moira',
            'Tessa',
            'Fiona'
        ];
        
        // Try to find preferred voice
        let selectedVoice = null;
        for (const voiceName of preferredVoices) {
            selectedVoice = voices.find(v => v.name === voiceName || v.name.includes(voiceName));
            if (selectedVoice) {
                console.log('🎙️ Selected voice:', selectedVoice.name);
                break;
            }
        }
        
        // Fallback: Find any Enhanced/Premium voice first
        if (!selectedVoice) {
            selectedVoice = voices.find(v => 
                v.name.includes('Enhanced') || 
                v.name.includes('Premium')
            );
        }
        
        // Last resort: Find any natural-sounding English female voice
        if (!selectedVoice) {
            selectedVoice = voices.find(v => 
                v.lang.startsWith('en') && 
                (v.name.toLowerCase().includes('female') || 
                 !v.name.toLowerCase().includes('male'))
            );
        }
        
        if (selectedVoice) {
            utterance.voice = selectedVoice;
            console.log('🎙️ Using voice:', selectedVoice.name, '| Language:', selectedVoice.lang);
        } else {
            console.warn('⚠️ No preferred voice found, using default');
        }
        
        utterance.onstart = () => {
            this.isSpeaking = true;
            this.updateSpeakerIcon();
            this.updateAssistantStatus('🗣️ Speaking...');
        };
        
        utterance.onend = () => {
            this.isSpeaking = false;
            this.updateSpeakerIcon();
            if (this.isListening) {
                this.updateAssistantStatus('🎤 Listening for next question...');
            } else {
                this.updateAssistantStatus('Ready');
            }
        };
        
        this.synthesis.speak(utterance);
    }
    
    /**
     * Stop speaking
     */
    stopSpeaking() {
        if (this.synthesis) {
            this.synthesis.cancel();
            this.isSpeaking = false;
            this.updateSpeakerIcon();
        }
    }
    
    /**
     * Add message to chat UI
     */
    addMessageToChat(role, message) {
        const chatMessages = document.getElementById(`chat-messages-${this.roomId}`);
        if (!chatMessages) {
            console.warn(`Chat container not found: chat-messages-${this.roomId}`);
            return;
        }
        
        const messageDiv = document.createElement('div');
        messageDiv.className = `assistant-message ${role}`;
        messageDiv.textContent = message;
        
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    /**
     * Update UI elements
     */
    updateAssistantStatus(status) {
        const statusElement = document.getElementById(`assistant-status-${this.roomId}`);
        if (statusElement) {
            statusElement.textContent = status;
            
            // Add appropriate class for styling
            statusElement.className = 'assistant-status';
            if (status.includes('🎤') || status.includes('Listening')) {
                statusElement.classList.add('listening');
            } else if (status.includes('🤔') || status.includes('Thinking')) {
                statusElement.classList.add('thinking');
            } else if (status.includes('🗣️') || status.includes('Speaking')) {
                statusElement.classList.add('speaking');
            }
            
            console.log('📊 Status updated to:', status);
        }
    }
    
    updateMicButton() {
        const micButton = document.getElementById(`assistant-mic-${this.roomId}`);
        if (micButton) {
            if (this.isListening) {
                micButton.classList.add('listening');
                micButton.style.animation = 'pulse 1.5s infinite';
            } else {
                micButton.classList.remove('listening');
                micButton.style.animation = '';
            }
        }
    }
    
    updateSpeakerIcon() {
        const speakerButton = document.getElementById(`assistant-speaker-${this.roomId}`);
        if (speakerButton) {
            speakerButton.classList.toggle('speaking', this.isSpeaking);
        }
    }
}

// Store assistant instances
window.assistants = {};

/**
 * Initialize assistant for a room
 */
function initAssistant(roomId, roomData) {
    if (!window.assistants[roomId]) {
        window.assistants[roomId] = new SmartAssistant(roomId, roomData);
    }
    return window.assistants[roomId];
}

/**
 * Toggle assistant modal
 */
function toggleAssistant(roomId) {
    const modal = document.getElementById(`assistant_modal_${roomId}`);
    if (modal) {
        modal.style.display = modal.style.display === 'none' ? 'flex' : 'none';
    }
}

/**
 * Send text message
 */
function sendTextMessage(roomId) {
    const input = document.getElementById(`text_input_${roomId}`);
    if (!input) return;
    
    const query = input.value.trim();
    if (query) {
        const assistant = window.assistants[roomId];
        if (assistant) {
            assistant.handleUserQuery(query);
            input.value = '';
        }
    }
}

/**
 * Toggle voice input
 */
function toggleVoice(roomId) {
    const assistant = window.assistants[roomId];
    if (assistant) {
        assistant.toggleVoiceInput();
    }
}

/**
 * Toggle voice output
 */
function toggleSpeaker(roomId) {
    const assistant = window.assistants[roomId];
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
}
