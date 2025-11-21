/**
 * Voice Diagnostic Tool
 * Debug and fix voice synthesis issues
 */

class VoiceDiagnostic {
    constructor() {
        this.synthesis = window.speechSynthesis;
        this.voices = [];
        this.testResults = {};
    }
    
    /**
     * Run comprehensive voice diagnostics
     */
    async runDiagnostics() {
        console.log('🔍 VOICE DIAGNOSTICS STARTING...');
        console.log('=' * 50);
        
        // Test 1: Speech Synthesis Support
        this.testSpeechSynthesisSupport();
        
        // Test 2: Available Voices
        await this.testAvailableVoices();
        
        // Test 3: Volume and Audio
        this.testAudioSettings();
        
        // Test 4: Browser Permissions
        this.testBrowserPermissions();
        
        // Test 5: Simple Voice Test
        await this.testBasicVoice();
        
        // Display Results
        this.displayResults();
    }
    
    testSpeechSynthesisSupport() {
        console.log('🎤 Testing Speech Synthesis Support...');
        
        if (!window.speechSynthesis) {
            this.testResults.speechSynthesis = {
                supported: false,
                issue: 'Speech Synthesis API not available',
                solution: 'Use Chrome, Edge, or Safari browser'
            };
            return;
        }
        
        this.testResults.speechSynthesis = {
            supported: true,
            message: 'Speech Synthesis API available'
        };
        
        console.log('✅ Speech Synthesis supported');
    }
    
    async testAvailableVoices() {
        console.log('🗣️ Testing Available Voices...');
        
        return new Promise((resolve) => {
            // Voices might load asynchronously
            const checkVoices = () => {
                this.voices = this.synthesis.getVoices();
                
                if (this.voices.length === 0) {
                    setTimeout(checkVoices, 100);
                    return;
                }
                
                console.log(`Found ${this.voices.length} voices:`);
                this.voices.forEach((voice, index) => {
                    console.log(`  ${index + 1}. ${voice.name} (${voice.lang})`);
                });
                
                // Find English voices
                const englishVoices = this.voices.filter(voice => voice.lang.includes('en'));
                const femaleVoices = englishVoices.filter(voice => 
                    voice.name.includes('Female') || 
                    voice.name.includes('Samantha') || 
                    voice.name.includes('Google')
                );
                
                this.testResults.voices = {
                    total: this.voices.length,
                    english: englishVoices.length,
                    female: femaleVoices.length,
                    recommended: femaleVoices[0] || englishVoices[0] || this.voices[0]
                };
                
                console.log(`✅ Found ${englishVoices.length} English voices`);
                resolve();
            };
            
            // Trigger voice loading
            this.synthesis.getVoices();
            if ('onvoiceschanged' in this.synthesis) {
                this.synthesis.onvoiceschanged = checkVoices;
            }
            checkVoices();
        });
    }
    
    testAudioSettings() {
        console.log('🔊 Testing Audio Settings...');
        
        // Check if audio context is allowed
        try {
            const audioContext = new (window.AudioContext || window.webkitAudioContext)();
            
            this.testResults.audio = {
                contextSupported: true,
                state: audioContext.state,
                sampleRate: audioContext.sampleRate
            };
            
            if (audioContext.state === 'suspended') {
                console.log('⚠️ Audio context suspended - user interaction may be required');
                this.testResults.audio.issue = 'Audio context suspended';
                this.testResults.audio.solution = 'User must interact with page first';
            } else {
                console.log('✅ Audio context active');
            }
            
            audioContext.close();
        } catch (error) {
            console.log('❌ Audio context error:', error);
            this.testResults.audio = {
                contextSupported: false,
                error: error.message
            };
        }
    }
    
    testBrowserPermissions() {
        console.log('🔐 Testing Browser Permissions...');
        
        const userAgent = navigator.userAgent;
        const browser = this.detectBrowser();
        
        this.testResults.browser = {
            name: browser,
            userAgent: userAgent,
            https: location.protocol === 'https:',
            localhost: location.hostname === 'localhost' || location.hostname === '127.0.0.1'
        };
        
        if (browser === 'Chrome' || browser === 'Edge') {
            console.log('✅ Recommended browser detected');
        } else if (browser === 'Safari') {
            console.log('⚠️ Safari - some voice features may be limited');
        } else if (browser === 'Firefox') {
            console.log('⚠️ Firefox - speech synthesis may be limited');
        } else {
            console.log('❌ Unsupported browser - use Chrome, Edge, or Safari');
        }
    }
    
    async testBasicVoice() {
        console.log('🎵 Testing Basic Voice Output...');
        
        return new Promise((resolve) => {
            if (!this.synthesis) {
                this.testResults.voiceTest = { success: false, error: 'No speech synthesis' };
                resolve();
                return;
            }
            
            const testText = "Voice test successful";
            const utterance = new SpeechSynthesisUtterance(testText);
            
            // Use recommended voice
            if (this.testResults.voices && this.testResults.voices.recommended) {
                utterance.voice = this.testResults.voices.recommended;
            }
            
            utterance.volume = 1.0;
            utterance.rate = 1.0;
            utterance.pitch = 1.0;
            
            utterance.onstart = () => {
                console.log('🔊 Voice test started');
                this.testResults.voiceTest = { 
                    success: true, 
                    message: 'Voice output working',
                    voice: utterance.voice ? utterance.voice.name : 'default'
                };
            };
            
            utterance.onend = () => {
                console.log('✅ Voice test completed');
                resolve();
            };
            
            utterance.onerror = (event) => {
                console.log('❌ Voice test failed:', event.error);
                this.testResults.voiceTest = { 
                    success: false, 
                    error: event.error,
                    solution: 'Check browser audio settings and permissions'
                };
                resolve();
            };
            
            // Add timeout
            setTimeout(() => {
                if (!this.testResults.voiceTest) {
                    console.log('⏰ Voice test timeout');
                    this.testResults.voiceTest = { 
                        success: false, 
                        error: 'timeout',
                        solution: 'Voice synthesis may be blocked or disabled'
                    };
                    resolve();
                }
            }, 5000);
            
            try {
                this.synthesis.speak(utterance);
            } catch (error) {
                console.log('❌ Failed to start voice test:', error);
                this.testResults.voiceTest = { 
                    success: false, 
                    error: error.message 
                };
                resolve();
            }
        });
    }
    
    detectBrowser() {
        const ua = navigator.userAgent;
        if (ua.includes('Chrome')) return 'Chrome';
        if (ua.includes('Firefox')) return 'Firefox';
        if (ua.includes('Safari') && !ua.includes('Chrome')) return 'Safari';
        if (ua.includes('Edge')) return 'Edge';
        return 'Unknown';
    }
    
    displayResults() {
        console.log('\n📊 VOICE DIAGNOSTICS RESULTS');
        console.log('=' * 40);
        
        // Speech Synthesis
        const ss = this.testResults.speechSynthesis;
        console.log(`\n🎤 Speech Synthesis: ${ss.supported ? '✅ Supported' : '❌ Not Supported'}`);
        if (ss.issue) console.log(`   Issue: ${ss.issue}`);
        if (ss.solution) console.log(`   Solution: ${ss.solution}`);
        
        // Voices
        const v = this.testResults.voices;
        if (v) {
            console.log(`\n🗣️ Voices: ${v.total} total, ${v.english} English`);
            if (v.recommended) {
                console.log(`   Recommended: ${v.recommended.name} (${v.recommended.lang})`);
            }
        }
        
        // Audio
        const a = this.testResults.audio;
        if (a) {
            console.log(`\n🔊 Audio: ${a.contextSupported ? '✅ Supported' : '❌ Not Supported'}`);
            if (a.state) console.log(`   State: ${a.state}`);
            if (a.issue) console.log(`   Issue: ${a.issue}`);
            if (a.solution) console.log(`   Solution: ${a.solution}`);
        }
        
        // Browser
        const b = this.testResults.browser;
        console.log(`\n🌐 Browser: ${b.name}`);
        console.log(`   HTTPS: ${b.https ? '✅' : '❌'}`);
        console.log(`   Localhost: ${b.localhost ? '✅' : '❌'}`);
        
        // Voice Test
        const vt = this.testResults.voiceTest;
        console.log(`\n🎵 Voice Test: ${vt.success ? '✅ Success' : '❌ Failed'}`);
        if (vt.voice) console.log(`   Voice Used: ${vt.voice}`);
        if (vt.error) console.log(`   Error: ${vt.error}`);
        if (vt.solution) console.log(`   Solution: ${vt.solution}`);
        
        // Overall Assessment
        this.showFixSuggestions();
    }
    
    showFixSuggestions() {
        console.log('\n🔧 SUGGESTED FIXES:');
        console.log('=' * 20);
        
        const issues = [];
        
        if (!this.testResults.speechSynthesis?.supported) {
            issues.push('❌ Use Chrome, Edge, or Safari browser');
        }
        
        if (this.testResults.audio?.issue) {
            issues.push('⚠️ Click somewhere on the page to enable audio');
        }
        
        if (!this.testResults.voiceTest?.success) {
            issues.push('🔊 Check system volume and browser audio settings');
            issues.push('🔐 Check browser permissions for audio');
        }
        
        if (this.testResults.browser?.name === 'Firefox') {
            issues.push('🦊 Firefox has limited speech synthesis - try Chrome');
        }
        
        if (!this.testResults.browser?.https && !this.testResults.browser?.localhost) {
            issues.push('🔒 Use HTTPS or localhost for better audio support');
        }
        
        if (issues.length === 0) {
            console.log('✅ No issues detected - voice should be working!');
            console.log('💡 If you still can\'t hear voice:');
            console.log('   • Check system volume');
            console.log('   • Check browser tab audio settings');
            console.log('   • Try refreshing the page');
        } else {
            issues.forEach((issue, index) => {
                console.log(`${index + 1}. ${issue}`);
            });
        }
        
        console.log('\n🎯 Quick Test: Run testVoiceNow() to test voice immediately');
    }
    
    // Quick test function
    testVoiceNow() {
        const utterance = new SpeechSynthesisUtterance('Hello! Voice is working correctly.');
        utterance.volume = 1.0;
        utterance.rate = 0.9;
        
        if (this.testResults.voices?.recommended) {
            utterance.voice = this.testResults.voices.recommended;
        }
        
        utterance.onstart = () => console.log('🔊 Speaking...');
        utterance.onend = () => console.log('✅ Voice test complete');
        utterance.onerror = (e) => console.log('❌ Voice error:', e.error);
        
        this.synthesis.speak(utterance);
        console.log('🎵 Voice test started - you should hear speech now');
    }
}

// Global diagnostic instance
window.voiceDiagnostic = new VoiceDiagnostic();

// Quick access functions
window.testVoice = () => window.voiceDiagnostic.runDiagnostics();
window.testVoiceNow = () => window.voiceDiagnostic.testVoiceNow();

console.log('🔧 Voice Diagnostic Tool Loaded!');
console.log('Run testVoice() to diagnose voice issues');
console.log('Run testVoiceNow() for quick voice test');