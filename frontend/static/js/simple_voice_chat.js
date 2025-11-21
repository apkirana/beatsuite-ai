/**
 * Simple Voice Chat - Uses Web Speech API + Local LLM
 * Fallback solution when Gemini Live is not available
 */

class SimpleVoiceChat {
    constructor(roomId, roomData) {
        this.roomId = roomId;
        this.roomData = roomData;
        this.isActive = false;
        this.recognition = null;
        this.synthesis = window.speechSynthesis;
        this.isListening = false;
        this.isSpeaking = false;
        
        // Check browser support
        this.hasWebSpeech = this.checkWebSpeechSupport();
    }
    
    checkWebSpeechSupport() {
        const hasRecognition = !!(window.SpeechRecognition || window.webkitSpeechRecognition);
        const hasSynthesis = !!window.speechSynthesis;
        
        console.log('🎤 Speech Recognition:', hasRecognition ? 'Supported' : 'Not supported');
        console.log('🔊 Speech Synthesis:', hasSynthesis ? 'Supported' : 'Not supported');
        
        return hasRecognition && hasSynthesis;
    }
    
    async start() {
        if (!this.hasWebSpeech) {
            this.updateUI('error', 'Voice chat not supported in this browser');
            return;
        }
        
        try {
            console.log('🚀 Starting Simple Voice Chat for room:', this.roomId);
            this.updateUI('connecting', 'Initializing voice chat...');
            
            this.setupSpeechRecognition();
            this.isActive = true;
            this.startListening();
            
        } catch (error) {
            console.error('❌ Failed to start voice chat:', error);
            this.updateUI('error', error.message);
        }
    }
    
    setupSpeechRecognition() {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        this.recognition = new SpeechRecognition();
        
        this.recognition.continuous = false;
        this.recognition.interimResults = false;
        this.recognition.lang = 'en-US';
        
        this.recognition.onstart = () => {
            console.log('🎤 Speech recognition started');
            this.isListening = true;
            this.updateUI('listening', 'Listening... speak now');
        };
        
        this.recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            console.log('💬 User said:', transcript);
            this.displayTranscript('You', transcript);
            this.processUserInput(transcript);
        };
        
        this.recognition.onerror = (event) => {
            console.error('❌ Speech recognition error:', event.error);
            if (event.error === 'not-allowed') {
                this.updateUI('error', 'Microphone access denied. Please allow microphone access.');
            } else {
                this.updateUI('error', 'Speech recognition error: ' + event.error);
            }
            this.isListening = false;
        };
        
        this.recognition.onend = () => {
            console.log('🎤 Speech recognition ended');
            this.isListening = false;
            if (this.isActive && !this.isSpeaking) {
                // Restart listening after a short delay
                setTimeout(() => {
                    if (this.isActive) {
                        this.startListening();
                    }
                }, 1000);
            }
        };
    }
    
    startListening() {
        if (this.isListening || this.isSpeaking || !this.isActive) return;
        
        try {
            this.recognition.start();
        } catch (error) {
            console.error('❌ Error starting recognition:', error);
            setTimeout(() => {
                if (this.isActive) this.startListening();
            }, 2000);
        }
    }
    
    async processUserInput(userText) {
        try {
            this.updateUI('thinking', 'AI is thinking...');
            
            // Get AI response using the existing chat API
            const API_BASE = window.API_BASE || '/api';
            const response = await fetch(`${API_BASE}/ai/chat/${this.roomId}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include',
                body: JSON.stringify({ 
                    message: `Voice chat: ${userText}`,
                    context: 'voice_conversation'
                })
            });
            
            if (!response.ok) {
                throw new Error(`AI request failed: ${response.status}`);
            }
            
            const data = await response.json();
            
            if (data.success && data.ai_response) {
                this.displayTranscript('AI', data.ai_response);
                await this.speakText(data.ai_response);
            } else {
                throw new Error('No AI response received');
            }
            
        } catch (error) {
            console.error('❌ Error processing user input:', error);
            const errorMsg = 'Sorry, I had trouble understanding. Could you please try again?';
            this.displayTranscript('AI', errorMsg);
            await this.speakText(errorMsg);
        }
    }
    
    async speakText(text) {
        if (!this.synthesis) return;
        
        // Stop current speech if any
        this.synthesis.cancel();
        
        return new Promise((resolve) => {
            const utterance = new SpeechSynthesisUtterance(text);
            
            // Use a natural voice if available
            const voices = this.synthesis.getVoices();
            const preferredVoice = voices.find(voice => 
                voice.name.includes('Samantha') || 
                voice.name.includes('Karen') ||
                voice.name.includes('Natural') ||
                (voice.lang.startsWith('en') && voice.localService)
            );
            
            if (preferredVoice) {
                utterance.voice = preferredVoice;
            }
            
            utterance.rate = 0.9;
            utterance.pitch = 1.0;
            utterance.volume = 0.8;
            
            utterance.onstart = () => {
                console.log('🔊 AI speaking:', text.substring(0, 50) + '...');
                this.isSpeaking = true;
                this.updateUI('speaking', 'AI is speaking...');
            };
            
            utterance.onend = () => {
                console.log('✅ AI finished speaking');
                this.isSpeaking = false;
                if (this.isActive) {
                    this.updateUI('listening', 'Your turn - speak now');
                    // Resume listening after speech
                    setTimeout(() => {
                        if (this.isActive) this.startListening();
                    }, 500);
                }
                resolve();
            };
            
            utterance.onerror = (error) => {
                console.error('❌ Speech synthesis error:', error);
                this.isSpeaking = false;
                resolve();
            };
            
            this.synthesis.speak(utterance);
        });
    }
    
    displayTranscript(speaker, text) {
        const transcriptEl = document.getElementById(`gemini-live-transcript-${this.roomId}`);
        if (transcriptEl) {
            const messageEl = document.createElement('div');
            messageEl.style.cssText = `
                padding: 8px 12px;
                margin-bottom: 6px;
                border-radius: 8px;
                font-size: 14px;
                background: ${speaker === 'AI' ? 'rgba(139, 92, 246, 0.3)' : 'rgba(59, 130, 246, 0.3)'};
                color: white;
                border-left: 3px solid ${speaker === 'AI' ? '#8b5cf6' : '#3b82f6'};
            `;
            messageEl.innerHTML = `<strong>${speaker}:</strong> ${text}`;
            transcriptEl.appendChild(messageEl);
            transcriptEl.scrollTop = transcriptEl.scrollHeight;
        }
    }
    
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
                    break;
                case 'listening':
                    icon = '🎤';
                    color = '#3b82f6';
                    break;
                case 'thinking':
                    icon = '🤔';
                    color = '#8b5cf6';
                    break;
                case 'speaking':
                    icon = '🔊';
                    color = '#10b981';
                    break;
                case 'error':
                    icon = '❌';
                    color = '#ef4444';
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
    
    stop() {
        console.log('🛑 Stopping Simple Voice Chat...');
        
        this.isActive = false;
        this.isListening = false;
        this.isSpeaking = false;
        
        // Stop speech recognition
        if (this.recognition) {
            this.recognition.stop();
        }
        
        // Stop speech synthesis
        if (this.synthesis) {
            this.synthesis.cancel();
        }
        
        this.updateUI('inactive', 'Disconnected');
        console.log('✅ Simple Voice Chat stopped');
    }
    
    toggle() {
        console.log('🔄 Toggle called, current state:', this.isActive);
        if (this.isActive) {
            this.stop();
        } else {
            this.start();
        }
    }
}

// Export for use
console.log('✅ SimpleVoiceChat class loaded');
window.SimpleVoiceChat = SimpleVoiceChat;