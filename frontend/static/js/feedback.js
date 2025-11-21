/**
 * Feedback System UI Component
 * Handles feedback collection, submission, and display
 * Integrates with agent memory for adaptive behavior
 */

class FeedbackSystem {
    constructor() {
        this.feedbackAPI = '/api/feedback';
        this.currentPatientId = null;
        this.feedbackModalOpen = false;
        this.initializeEventListeners();
    }
    
    /**
     * Initialize feedback UI event listeners
     */
    initializeEventListeners() {
        // Listen for room card interactions to show feedback button
        document.addEventListener('roomCardCreated', (e) => {
            this.attachFeedbackButton(e.detail.roomId);
        });
    }
    
    /**
     * Attach feedback button to room card
     */
    attachFeedbackButton(roomId) {
        const roomCard = document.querySelector(`[data-room-id="${roomId}"]`);
        if (roomCard) {
            // Add feedback button to existing card
            const buttonsContainer = roomCard.querySelector('.room-card-buttons') || 
                                    roomCard.querySelector('.action-buttons');
            if (buttonsContainer && !roomCard.querySelector('.feedback-button')) {
                const feedbackBtn = document.createElement('button');
                feedbackBtn.className = 'feedback-button';
                feedbackBtn.innerHTML = '💭 Feedback';
                feedbackBtn.title = 'Rate this interaction';
                feedbackBtn.onclick = (e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    this.showFeedbackModal(roomId);
                };
                buttonsContainer.appendChild(feedbackBtn);
            }
        }
    }
    
    /**
     * Show feedback modal for a room
     */
    showFeedbackModal(roomId) {
        const room = window.allRoomsData?.[roomId];
        if (!room) {
            console.error('Room data not found');
            return;
        }
        
        const patientName = room.patient_name || 'Patient';
        this.currentPatientId = room.patient_id;
        
        let modal = document.getElementById('feedbackModal');
        if (!modal) {
            modal = this.createFeedbackModal();
            document.body.appendChild(modal);
        }
        
        // Update modal content
        modal.querySelector('.feedback-patient-name').textContent = patientName;
        modal.querySelector('.feedback-room-id').textContent = room.room_number || roomId;
        
        // Reset form
        modal.querySelector('form').reset();
        modal.querySelector('.feedback-rating').value = 'positive';
        
        modal.style.display = 'flex';
        this.feedbackModalOpen = true;
    }
    
    /**
     * Create feedback modal HTML
     */
    createFeedbackModal() {
        const modal = document.createElement('div');
        modal.id = 'feedbackModal';
        modal.className = 'feedback-modal-overlay';
        modal.innerHTML = `
            <div class="feedback-modal">
                <div class="feedback-modal-header">
                    <h2>📝 Rate This Interaction</h2>
                    <button class="modal-close" onclick="window.feedbackSystem.closeFeedbackModal()">✕</button>
                </div>
                
                <div class="feedback-modal-body">
                    <div class="feedback-info">
                        <p><strong>Patient:</strong> <span class="feedback-patient-name">-</span></p>
                        <p><strong>Room:</strong> <span class="feedback-room-id">-</span></p>
                    </div>
                    
                    <form id="feedbackForm" onsubmit="window.feedbackSystem.submitFeedback(event)">
                        <!-- Interaction Type -->
                        <div class="form-group">
                            <label for="interactionType">What type of interaction?</label>
                            <select id="interactionType" name="interaction_type" required>
                                <option value="">-- Select --</option>
                                <option value="music_suggestion">🎵 Music Suggestion</option>
                                <option value="lighting">💡 Lighting Adjustment</option>
                                <option value="environment_control">🌡️ Environment Control</option>
                                <option value="pain_management">🤕 Pain Management</option>
                                <option value="activity_suggestion">🎮 Activity Suggestion</option>
                                <option value="general_interaction">💬 General Interaction</option>
                            </select>
                        </div>
                        
                        <!-- Specific Action Taken -->
                        <div class="form-group">
                            <label for="actionTaken">What was the specific action?</label>
                            <input type="text" id="actionTaken" name="action_taken" 
                                   placeholder="e.g., Played Disney Classics playlist"
                                   required>
                        </div>
                        
                        <!-- Situation/Context -->
                        <div class="form-group">
                            <label for="situation">What was the situation?</label>
                            <input type="text" id="situation" name="situation"
                                   placeholder="e.g., Patient was awake in the afternoon"
                                   required>
                        </div>
                        
                        <!-- Rating -->
                        <div class="form-group">
                            <label>How would you rate this interaction?</label>
                            <div class="rating-buttons">
                                <button type="button" class="rating-btn negative" 
                                        data-rating="negative" title="Didn't work well">
                                    👎 Didn't Work
                                </button>
                                <button type="button" class="rating-btn neutral" 
                                        data-rating="neutral" title="Neutral">
                                    😐 Neutral
                                </button>
                                <button type="button" class="rating-btn positive" 
                                        data-rating="positive" title="Worked great">
                                    👍 Worked Great
                                </button>
                            </div>
                            <input type="hidden" id="feedbackRating" name="rating" 
                                   class="feedback-rating" value="positive">
                        </div>
                        
                        <!-- Numeric Score (Optional) -->
                        <div class="form-group">
                            <label for="ratingScore">Rate on a scale (1-5) - Optional</label>
                            <div class="rating-scale">
                                <input type="range" id="ratingScore" name="rating_score" 
                                       min="1" max="5" value="3">
                                <div class="scale-labels">
                                    <span>1 (Bad)</span>
                                    <span id="scoreDisplay">3 (Okay)</span>
                                    <span>5 (Great)</span>
                                </div>
                            </div>
                        </div>
                        
                        <!-- Comment -->
                        <div class="form-group">
                            <label for="userComment">Any additional comments?</label>
                            <textarea id="userComment" name="user_comment" 
                                      placeholder="e.g., Patient smiled and seemed much happier..."
                                      rows="3"></textarea>
                        </div>
                        
                        <!-- Hidden patient ID -->
                        <input type="hidden" id="patientId" name="patient_id">
                        
                        <!-- Submit Button -->
                        <div class="form-actions">
                            <button type="button" class="btn-secondary" 
                                    onclick="window.feedbackSystem.closeFeedbackModal()">
                                Cancel
                            </button>
                            <button type="submit" class="btn-primary">
                                Submit Feedback
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        `;
        
        // Add event listeners
        const ratingBtns = modal.querySelectorAll('.rating-btn');
        ratingBtns.forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                ratingBtns.forEach(b => b.classList.remove('selected'));
                btn.classList.add('selected');
                modal.querySelector('.feedback-rating').value = btn.dataset.rating;
            });
        });
        
        // Update score display
        modal.querySelector('#ratingScore').addEventListener('change', (e) => {
            const scores = ['', 'Very Bad', 'Bad', 'Okay', 'Good', 'Excellent'];
            modal.querySelector('#scoreDisplay').textContent = 
                `${e.target.value} (${scores[e.target.value]})`;
        });
        
        // Close on background click
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                this.closeFeedbackModal();
            }
        });
        
        return modal;
    }
    
    /**
     * Close feedback modal
     */
    closeFeedbackModal() {
        const modal = document.getElementById('feedbackModal');
        if (modal) {
            modal.style.display = 'none';
            this.feedbackModalOpen = false;
        }
    }
    
    /**
     * Submit feedback via API
     */
    async submitFeedback(event) {
        event.preventDefault();
        
        const form = event.target;
        const submitBtn = form.querySelector('button[type="submit"]');
        submitBtn.disabled = true;
        submitBtn.textContent = 'Submitting...';
        
        try {
            const feedbackData = {
                patient_id: this.currentPatientId,
                interaction_type: form.querySelector('#interactionType').value,
                rating: form.querySelector('.feedback-rating').value,
                rating_score: parseInt(form.querySelector('#ratingScore').value) || null,
                user_comment: form.querySelector('#userComment').value,
                interaction_context: {
                    action: form.querySelector('#actionTaken').value,
                    situation: form.querySelector('#situation').value,
                    timestamp: new Date().toISOString()
                }
            };
            
            const response = await fetch(`${this.feedbackAPI}/submit`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${window.authUtils.getToken()}`
                },
                body: JSON.stringify(feedbackData)
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.showSuccessNotification('Feedback submitted successfully! 🎉');
                this.closeFeedbackModal();
                
                // Optionally refresh adaptation recommendations
                this.refreshAdaptationRecommendations(this.currentPatientId);
            } else {
                this.showErrorNotification(`Error: ${result.error || 'Failed to submit feedback'}`);
            }
        } catch (error) {
            console.error('Error submitting feedback:', error);
            this.showErrorNotification('Failed to submit feedback. Please try again.');
        } finally {
            submitBtn.disabled = false;
            submitBtn.textContent = 'Submit Feedback';
        }
    }
    
    /**
     * Show quick feedback buttons in a room context (simplified version)
     */
    showQuickFeedback(patientId, interactionType, action) {
        const quickFeedbackId = `quick-feedback-${patientId}-${Date.now()}`;
        
        const container = document.createElement('div');
        container.id = quickFeedbackId;
        container.className = 'quick-feedback-container';
        container.innerHTML = `
            <div class="quick-feedback">
                <span class="quick-feedback-text">Was that helpful?</span>
                <button class="quick-fb-btn negative" data-rating="negative">👎</button>
                <button class="quick-fb-btn neutral" data-rating="neutral">😐</button>
                <button class="quick-fb-btn positive" data-rating="positive">👍</button>
            </div>
        `;
        
        document.body.appendChild(container);
        
        const buttons = container.querySelectorAll('.quick-fb-btn');
        buttons.forEach(btn => {
            btn.addEventListener('click', async (e) => {
                e.preventDefault();
                const rating = btn.dataset.rating;
                
                const feedbackData = {
                    patient_id: patientId,
                    interaction_type: interactionType,
                    rating: rating,
                    interaction_context: {
                        action: action,
                        timestamp: new Date().toISOString()
                    }
                };
                
                try {
                    const response = await fetch(`${this.feedbackAPI}/submit`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'Authorization': `Bearer ${window.authUtils.getToken()}`
                        },
                        body: JSON.stringify(feedbackData)
                    });
                    
                    const result = await response.json();
                    if (result.success) {
                        container.classList.add('submitted');
                        setTimeout(() => container.remove(), 2000);
                    }
                } catch (error) {
                    console.error('Error submitting quick feedback:', error);
                }
            });
        });
        
        // Auto-remove after 10 seconds
        setTimeout(() => {
            if (container.parentNode) {
                container.remove();
            }
        }, 10000);
    }
    
    /**
     * Refresh adaptation recommendations after feedback
     */
    async refreshAdaptationRecommendations(patientId) {
        try {
            const response = await fetch(
                `${this.feedbackAPI}/pattern-analysis/${patientId}`,
                {
                    headers: {
                        'Authorization': `Bearer ${window.authUtils.getToken()}`
                    }
                }
            );
            
            const result = await response.json();
            
            if (result.success && result.patterns) {
                console.log('Adaptation patterns updated:', result.patterns);
                // Could emit event or update UI
                document.dispatchEvent(new CustomEvent('adaptationPatternsUpdated', {
                    detail: { patientId, patterns: result.patterns }
                }));
            }
        } catch (error) {
            console.error('Error refreshing recommendations:', error);
        }
    }
    
    /**
     * Display feedback summary for a patient
     */
    async showFeedbackSummary(patientId) {
        try {
            const response = await fetch(
                `${this.feedbackAPI}/summary/${patientId}`,
                {
                    headers: {
                        'Authorization': `Bearer ${window.authUtils.getToken()}`
                    }
                }
            );
            
            const summary = await response.json();
            
            if (summary.success) {
                this.displayFeedbackSummaryModal(summary);
            }
        } catch (error) {
            console.error('Error fetching feedback summary:', error);
        }
    }
    
    /**
     * Display feedback summary in modal
     */
    displayFeedbackSummaryModal(summary) {
        let modal = document.getElementById('feedbackSummaryModal');
        if (!modal) {
            modal = document.createElement('div');
            modal.id = 'feedbackSummaryModal';
            modal.className = 'feedback-modal-overlay';
            document.body.appendChild(modal);
        }
        
        const satisfactionColor = summary.satisfaction_rate >= 75 ? '#10B981' : 
                                 summary.satisfaction_rate >= 50 ? '#F59E0B' : '#EF4444';
        
        modal.innerHTML = `
            <div class="feedback-modal">
                <div class="feedback-modal-header">
                    <h2>📊 Feedback Summary</h2>
                    <button class="modal-close" onclick="document.getElementById('feedbackSummaryModal').style.display='none'">✕</button>
                </div>
                
                <div class="feedback-modal-body">
                    <div class="summary-grid">
                        <div class="summary-card">
                            <div class="summary-value" style="color: ${satisfactionColor}">
                                ${summary.satisfaction_rate.toFixed(1)}%
                            </div>
                            <div class="summary-label">Satisfaction Rate</div>
                        </div>
                        
                        <div class="summary-card">
                            <div class="summary-value">${summary.total_feedback_count}</div>
                            <div class="summary-label">Total Feedback</div>
                        </div>
                        
                        <div class="summary-card">
                            <div class="summary-value" style="color: #10B981">
                                ${summary.feedback_distribution.positive}
                            </div>
                            <div class="summary-label">Positive</div>
                        </div>
                        
                        <div class="summary-card">
                            <div class="summary-value" style="color: #EF4444">
                                ${summary.feedback_distribution.negative}
                            </div>
                            <div class="summary-label">Negative</div>
                        </div>
                    </div>
                    
                    <div class="summary-section">
                        <h3>Most Liked Actions</h3>
                        <div class="action-list">
                            ${summary.most_liked_actions.length > 0 ? 
                                summary.most_liked_actions.map(a => 
                                    `<span class="action-tag positive">👍 ${a}</span>`
                                ).join('') :
                                '<p>No data yet</p>'
                            }
                        </div>
                    </div>
                    
                    <div class="summary-section">
                        <h3>Least Liked Actions</h3>
                        <div class="action-list">
                            ${summary.least_liked_actions.length > 0 ? 
                                summary.least_liked_actions.map(a => 
                                    `<span class="action-tag negative">👎 ${a}</span>`
                                ).join('') :
                                '<p>No data yet</p>'
                            }
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        modal.style.display = 'flex';
    }
    
    /**
     * Show notification
     */
    showSuccessNotification(message) {
        this.showNotification(message, 'success');
    }
    
    showErrorNotification(message) {
        this.showNotification(message, 'error');
    }
    
    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 15px 20px;
            border-radius: 8px;
            background: ${type === 'success' ? '#10B981' : type === 'error' ? '#EF4444' : '#3B82F6'};
            color: white;
            z-index: 10000;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            animation: slideIn 0.3s ease;
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }
}

// Global instance
window.feedbackSystem = new FeedbackSystem();

// Add styles for animations
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
