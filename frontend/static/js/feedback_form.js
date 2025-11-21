document.addEventListener('DOMContentLoaded', async () => {
    let selectedFeedback = null;
    let selectedPatientId = null;
    const goodBtn = document.getElementById('goodBtn');
    const badBtn = document.getElementById('badBtn');
    const submitBtn = document.getElementById('submitBtn');
    const summaryText = document.getElementById('summaryText');
    const feedbackStatus = document.getElementById('feedbackStatus');
    const patientSelect = document.getElementById('patientSelect');

    // Check authentication
    let currentUser = null;
    try {
        const userData = await window.api.getCurrentUser();
        currentUser = userData.user;
        if (!currentUser) {
            window.location.href = '/login';
            return;
        }
    } catch (error) {
        console.error('Auth check failed:', error);
        window.location.href = '/login';
        return;
    }

    // Load patient list
    await loadPatients(currentUser);

    // Patient selector change handler
    patientSelect.addEventListener('change', async (e) => {
        selectedPatientId = e.target.value;
        if (selectedPatientId) {
            await loadSmartWatchData(selectedPatientId);
        }
    });

    // Load smartwatch data and AI analysis for current user
    if (currentUser.role === 'patient') {
        selectedPatientId = currentUser.user_id;
        await loadSmartWatchData(selectedPatientId);
    } else {
        // For non-patient users, show placeholder until a patient is selected
        document.getElementById('aiReasoning').textContent = 'Select a patient to view their current status';
    }

    // Feedback button handlers
    goodBtn.addEventListener('click', () => {
        selectFeedback('positive', goodBtn, badBtn);
        selectedFeedback = 'positive';
    });

    badBtn.addEventListener('click', () => {
        selectFeedback('negative', badBtn, goodBtn);
        selectedFeedback = 'negative';
    });

    // Submit handler
    submitBtn.addEventListener('click', async () => {
        if (!selectedFeedback) {
            feedbackStatus.textContent = 'Please select Good or Not Good';
            feedbackStatus.className = 'feedback-status error';
            return;
        }

        if (!selectedPatientId) {
            feedbackStatus.textContent = 'Please select a patient';
            feedbackStatus.className = 'feedback-status error';
            return;
        }

        submitBtn.disabled = true;
        feedbackStatus.textContent = 'Submitting...';
        feedbackStatus.className = 'feedback-status';

        try {
            const summary = summaryText.value.trim();
            const response = await fetch('/api/feedback', {
                method: 'POST',
                credentials: 'include',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    patient_id: selectedPatientId,
                    interaction_summary: summary || `Environment rated as ${selectedFeedback}`,
                    feedback: selectedFeedback
                })
            });

            if (!response.ok) {
                throw new Error('Failed to submit feedback');
            }

            feedbackStatus.textContent = 'Thank you! Your feedback has been recorded.';
            feedbackStatus.className = 'feedback-status success';

            // Reset form after 2 seconds
            setTimeout(() => {
                selectedFeedback = null;
                goodBtn.classList.remove('active');
                badBtn.classList.remove('active');
                summaryText.value = '';
                feedbackStatus.textContent = '';
                submitBtn.disabled = false;
            }, 2000);

        } catch (error) {
            console.error('Feedback submission error:', error);
            feedbackStatus.textContent = 'Error submitting feedback. Please try again.';
            feedbackStatus.className = 'feedback-status error';
            submitBtn.disabled = false;
        }
    });

    function selectFeedback(type, activeBtn, inactiveBtn) {
        activeBtn.classList.add('active');
        inactiveBtn.classList.remove('active');
    }

    async function loadPatients(currentUser) {
        try {
            // Only show patient selector for admin/nurse/family users
            if (currentUser.role === 'patient') {
                // For patient users, hide the selector and auto-select themselves
                document.getElementById('patientSelector').style.display = 'none';
                selectedPatientId = currentUser.user_id;
                return;
            }

            const response = await fetch('/api/users', {
                credentials: 'include'
            });

            if (!response.ok) {
                console.error('Failed to fetch patients');
                return;
            }

            const data = await response.json();
            const patients = data.users || [];

            // Filter for patients only (check role field)
            const patientUsers = patients.filter(u => u.role === 'patient');

            if (patientUsers.length === 0) {
                patientSelect.innerHTML = '<option value="">No patients found</option>';
                return;
            }

            // Clear loading option and populate with actual patients
            patientSelect.innerHTML = '<option value="">Select a patient...</option>';
            patientUsers.forEach(patient => {
                const option = document.createElement('option');
                option.value = patient.user_id || patient.username;
                option.textContent = `${patient.full_name || patient.username} (${patient.user_id || patient.username})`;
                patientSelect.appendChild(option);
            });

        } catch (error) {
            console.error('Error loading patients:', error);
            patientSelect.innerHTML = '<option value="">Error loading patients</option>';
        }
    }

    async function loadSmartWatchData(patientId) {
        try {
            // Show loading indicator
            document.getElementById('loadingIndicator').style.display = 'inline-flex';

            // Reset values to loading state
            document.getElementById('hrValue').textContent = '--';
            document.getElementById('spo2Value').textContent = '--';
            document.getElementById('movementValue').textContent = '--';
            document.getElementById('batteryValue').textContent = '--';
            document.getElementById('aiReasoning').textContent = 'Loading patient data...';

            // Get smartwatch data
            const roomsResponse = await fetch('/api/rooms', {
                credentials: 'include'
            });

            if (!roomsResponse.ok) {
                console.error('Failed to fetch room data');
                document.getElementById('aiReasoning').textContent = 'No room data available for this patient';
                document.getElementById('loadingIndicator').style.display = 'none';
                return;
            }

            const rooms = await roomsResponse.json();
            let patientRoom = null;

            // Find room for current patient
            for (const room of rooms) {
                if (room.patient_id === patientId) {
                    patientRoom = room;
                    break;
                }
            }

            if (!patientRoom) {
                console.warn('No room data found for patient');
                document.getElementById('aiReasoning').textContent = 'No active room data for this patient';
                document.getElementById('loadingIndicator').style.display = 'none';
                return;
            }

            // Update smartwatch display with room data
            if (patientRoom.heart_rate !== undefined) {
                document.getElementById('hrValue').textContent = patientRoom.heart_rate;
            }
            if (patientRoom.oxygen_level !== undefined) {
                document.getElementById('spo2Value').textContent = patientRoom.oxygen_level;
            }

            // Try to get extended AI analysis with more details
            try {
                const testResponse = await fetch(`/api/test/current-vitals?patient_id=${patientId}`, {
                    credentials: 'include'
                });

                if (testResponse.ok) {
                    const testData = await testResponse.json();

                    if (testData.movement !== undefined) {
                        const movementPercent = Math.round(testData.movement * 100);
                        document.getElementById('movementValue').textContent = movementPercent;
                    }

                    // Update AI reasoning with full analysis
                    const reasoning = generateAIReasoning(patientRoom, testData);
                    document.getElementById('aiReasoning').textContent = reasoning;
                }
            } catch (e) {
                console.warn('Could not fetch extended vitals data:', e);
                // Fall back to room-only reasoning
                const reasoning = generateAIReasoning(patientRoom, {});
                document.getElementById('aiReasoning').textContent = reasoning;
            }

            // Try to get smartwatch specific battery level
            try {
                const smartwatchResponse = await fetch(`/api/smartwatch/${patientId}/current`, {
                    credentials: 'include'
                });

                if (smartwatchResponse.ok) {
                    const smartwatchData = await smartwatchResponse.json();
                    if (smartwatchData.battery_level !== undefined) {
                        document.getElementById('batteryValue').textContent = smartwatchData.battery_level;
                    }
                }
            } catch (e) {
                console.warn('Could not fetch smartwatch data:', e);
            }

        } catch (error) {
            console.error('Error loading smartwatch data:', error);
            // Use default values if data loading fails
            document.getElementById('aiReasoning').textContent = 'Unable to load patient data. Please try again.';
        } finally {
            // Hide loading indicator
            document.getElementById('loadingIndicator').style.display = 'none';
        }
    }

    function generateAIReasoning(room, testData) {
        const parts = [];

        // Heart rate analysis
        if (room.heart_rate) {
            if (room.heart_rate < 60) {
                parts.push('resting state');
            } else if (room.heart_rate < 85) {
                parts.push('normal activity level');
            } else {
                parts.push('elevated activity or stress');
            }
        }

        // Sleep stage analysis
        if (room.sleep_stage) {
            parts.push(`${room.sleep_stage.replace('_', ' ')}`);
        }

        // Pain detection
        if (room.pain_detected) {
            parts.push('pain detected - adjusting comfort settings');
        }

        // AI reasoning from the system
        if (room.current_ai_settings && room.current_ai_settings.ai_reasoning) {
            return room.current_ai_settings.ai_reasoning;
        }

        // Construct a meaningful message
        if (parts.length === 0) {
            return 'Environment is optimized for your current state. Please rate how it feels.';
        }

        return `You are in ${parts.join(', ')}. Environment has been adjusted accordingly. How does it feel?`;
    }
});
