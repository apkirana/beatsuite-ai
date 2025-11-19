/**
 * Patient Report Generator
 * Generates PDF reports for patient health data
 */

// Wait for jsPDF to load
if (typeof window.jspdf === 'undefined') {
    console.warn('jsPDF library not loaded yet. PDF generation will be available after page load.');
}

/**
 * Generate PDF report for a patient
 */
async function generatePatientReport(roomId) {
    // Check if jsPDF is available
    if (typeof window.jspdf === 'undefined') {
        showNotification('PDF library is still loading. Please try again in a moment.', 'error');
        return;
    }
    try {
        // Show loading indicator with AI message
        showReportLoading('Generating AI-powered health analysis...');
        
        // Find the room data
        const room = rooms.find(r => r.room_id === roomId);
        if (!room) {
            throw new Error('Room data not found');
        }
        
        // Fetch health history
        const historyResponse = await fetch(`/api/health-history/${room.patient_id}?hours=168`, {
            credentials: 'include'
        });
        
        if (!historyResponse.ok) {
            throw new Error('Failed to fetch health history');
        }
        
        const historyData = await historyResponse.json();
        
        // Fetch AI-generated report analysis
        let aiReport = null;
        try {
            console.log('🔍 Fetching AI report for patient:', room.patient_id);
            console.log('🔍 Full URL:', `/api/report-analysis/generate/${room.patient_id}`);
            
            const aiResponse = await fetch(`/api/report-analysis/generate/${room.patient_id}`, {
                credentials: 'include'
            });
            
            console.log('📡 AI API response status:', aiResponse.status);
            
            if (aiResponse.ok) {
                const aiData = await aiResponse.json();
                if (aiData.success) {
                    aiReport = aiData.report;
                    console.log('✅ AI report analysis loaded:', aiReport);
                } else {
                    console.warn('⚠️ AI report API returned success=false');
                }
            } else {
                console.warn('⚠️ AI report API returned error status:', aiResponse.status);
            }
        } catch (aiError) {
            console.error('❌ AI analysis error:', aiError);
        }
        
        // Create PDF
        const { jsPDF } = window.jspdf;
        const doc = new jsPDF();
        
        let currentY = 20;
        
        // Add header
        addReportHeader(doc, room);
        currentY = 30;
        
        // Add AI Executive Summary (if available)
        if (aiReport) {
            currentY = addAIExecutiveSummary(doc, aiReport, currentY);
            currentY += 10;
        }
        
        // Add patient information
        addPatientInfo(doc, room, currentY);
        currentY += 40;
        
        // Add current vitals
        addCurrentVitals(doc, room, currentY);
        currentY += 40;
        
        // Add AI Vital Signs Analysis (if available)
        if (aiReport) {
            currentY = addAIVitalAnalysis(doc, aiReport, currentY);
            currentY += 10;
        }
        
        // Add health status
        addHealthStatus(doc, room, currentY);
        currentY += 30;
        
        // Add AI Health Trends (if available)
        if (aiReport) {
            currentY = addAIHealthTrends(doc, aiReport, currentY);
            currentY += 10;
        }
        
        // Add AI status
        addAIStatus(doc, room, currentY);
        currentY += 30;
        
        // Add health history summary
        if (historyData.records && historyData.records.length > 0) {
            addHealthHistorySummary(doc, historyData.records, currentY);
            currentY += 35;
        }
        
        // Start new page for AI comprehensive analysis
        if (aiReport) {
            console.log('📄 Adding AI comprehensive analysis page...');
            console.log('aiReport data:', JSON.stringify(aiReport, null, 2));
            doc.addPage();
            currentY = 20;
            currentY = addAIComprehensiveAnalysis(doc, aiReport, currentY);
            console.log('✅ AI comprehensive analysis page completed');
        } else {
            console.warn('⚠️ No AI report available - skipping comprehensive analysis page');
        }
        
        // Add footer to all pages
        addReportFooter(doc);
        
        // Generate filename with timestamp
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, -5);
        const filename = `Patient_Report_${room.patient_name.replace(/\s+/g, '_')}_${timestamp}.pdf`;
        
        // Save the PDF
        doc.save(filename);
        
        // Hide loading indicator
        hideReportLoading();
        
        // Show success message
        showNotification('Report generated successfully!', 'success');
        
    } catch (error) {
        console.error('Error generating report:', error);
        hideReportLoading();
        showNotification('Failed to generate report. Please try again.', 'error');
    }
}

/**
 * Add report header
 */
function addReportHeader(doc, room) {
    // Title
    doc.setFontSize(20);
    doc.setFont(undefined, 'bold');
    doc.setTextColor(14, 165, 233); // Primary blue
    doc.text('PATIENT HEALTH REPORT', 105, 20, { align: 'center' });
    
    // Subtitle
    doc.setFontSize(12);
    doc.setFont(undefined, 'normal');
    doc.setTextColor(100, 116, 139);
    doc.text('Beat Suite AI - Prinses Máxima Centrum', 105, 28, { align: 'center' });
    
    // Line separator
    doc.setDrawColor(226, 232, 240);
    doc.setLineWidth(0.5);
    doc.line(20, 33, 190, 33);
}

/**
 * Add patient information
 */
function addPatientInfo(doc, room, yPos) {
    doc.setFontSize(14);
    doc.setFont(undefined, 'bold');
    doc.setTextColor(30, 41, 59);
    doc.text('Patient Information', 20, yPos);
    
    doc.setFontSize(11);
    doc.setFont(undefined, 'normal');
    doc.setTextColor(71, 85, 105);
    
    const infoLines = [
        `Room Number: ${room.room_number}`,
        `Patient Name: ${room.patient_name}`,
        `Patient ID: ${room.patient_id}`,
        `Report Generated: ${new Date().toLocaleString('en-US', { 
            year: 'numeric', 
            month: 'long', 
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        })}`
    ];
    
    infoLines.forEach((line, index) => {
        doc.text(line, 25, yPos + 8 + (index * 6));
    });
}

/**
 * Add current vitals
 */
function addCurrentVitals(doc, room, yPos) {
    doc.setFontSize(14);
    doc.setFont(undefined, 'bold');
    doc.setTextColor(30, 41, 59);
    doc.text('Current Vital Signs', 20, yPos);
    
    doc.setFontSize(11);
    doc.setFont(undefined, 'normal');
    doc.setTextColor(71, 85, 105);
    
    const tempCelsius = ((room.vitals.temperature - 32) * 5/9).toFixed(1);
    
    const vitals = [
        { label: 'Heart Rate', value: `${room.vitals.heart_rate} bpm`, normal: '60-100 bpm' },
        { label: 'Temperature', value: `${tempCelsius}°C`, normal: '36.5-37.5°C' },
        { label: 'Respiratory Rate', value: `${room.vitals.respiratory_rate}/min`, normal: '12-20/min' },
        { label: 'Blood Oxygen (SpO2)', value: `${room.vitals.spo2}%`, normal: '95-100%' }
    ];
    
    vitals.forEach((vital, index) => {
        const y = yPos + 8 + (index * 7);
        doc.setFont(undefined, 'bold');
        doc.text(`${vital.label}:`, 25, y);
        doc.setFont(undefined, 'normal');
        doc.text(vital.value, 70, y);
        doc.setTextColor(100, 116, 139);
        doc.setFontSize(9);
        doc.text(`(Normal: ${vital.normal})`, 100, y);
        doc.setFontSize(11);
        doc.setTextColor(71, 85, 105);
    });
}

/**
 * Add health status
 */
function addHealthStatus(doc, room, yPos) {
    doc.setFontSize(14);
    doc.setFont(undefined, 'bold');
    doc.setTextColor(30, 41, 59);
    doc.text('Health Status', 20, yPos);
    
    doc.setFontSize(11);
    doc.setFont(undefined, 'normal');
    
    // Determine health status
    const hr = room.vitals.heart_rate;
    const spo2 = room.vitals.spo2;
    const painDetected = room.current_state.pain_detected;
    
    let healthStatus = 'Stable';
    let statusColor = [16, 185, 129]; // Green
    
    if (painDetected || hr > 100 || spo2 < 95) {
        healthStatus = 'Needs Attention';
        statusColor = [255, 167, 38]; // Orange
    } else if (hr < 50 || hr > 110) {
        healthStatus = 'Alert';
        statusColor = [239, 68, 68]; // Red
    }
    
    doc.setTextColor(...statusColor);
    doc.setFont(undefined, 'bold');
    doc.text(`Status: ${healthStatus}`, 25, yPos + 8);
    
    doc.setTextColor(71, 85, 105);
    doc.setFont(undefined, 'normal');
    doc.text(`Sleep Stage: ${room.current_state.sleep_stage}`, 25, yPos + 15);
    
    if (painDetected) {
        doc.setTextColor(197, 48, 48);
        doc.text('⚠ Pain Detected', 25, yPos + 22);
    }
}

/**
 * Add AI status
 */
function addAIStatus(doc, room, yPos) {
    doc.setFontSize(14);
    doc.setFont(undefined, 'bold');
    doc.setTextColor(30, 41, 59);
    doc.text('AI Control Status', 20, yPos);
    
    doc.setFontSize(11);
    doc.setFont(undefined, 'normal');
    
    if (room.ai_control_active) {
        doc.setTextColor(16, 185, 129);
        doc.text('Status: AI ACTIVE', 25, yPos + 8);
        
        doc.setTextColor(71, 85, 105);
        
        // Get AI actions safely
        let actions;
        if (typeof getAIActionDescription === 'function') {
            actions = getAIActionDescription(room);
        } else {
            // Fallback if function not available
            actions = {
                light: room.ai_actions?.light_level || 'N/A',
                music: room.ai_actions?.music_state || 'N/A',
                reasoning: room.ai_actions?.reasoning || 'AI controlling environment based on patient state'
            };
        }
        
        doc.text(`Light: ${actions.light}`, 25, yPos + 15);
        doc.text(`Music: ${actions.music}`, 25, yPos + 21);
        doc.setFontSize(10);
        doc.text(`Reasoning: ${actions.reasoning}`, 25, yPos + 27, { maxWidth: 160 });
    } else {
        doc.setTextColor(255, 167, 38);
        doc.text('Status: MANUAL CONTROL', 25, yPos + 8);
        doc.setTextColor(71, 85, 105);
        doc.text('Staff controlling environment manually', 25, yPos + 15);
    }
}

/**
 * Add health history summary
 */
function addHealthHistorySummary(doc, records, yPos) {
    // Add new page if needed
    if (yPos > 240) {
        doc.addPage();
        yPos = 20;
    }
    
    doc.setFontSize(14);
    doc.setFont(undefined, 'bold');
    doc.setTextColor(30, 41, 59);
    doc.text('Health History Summary (Last 7 Days)', 20, yPos);
    
    doc.setFontSize(10);
    doc.setFont(undefined, 'normal');
    doc.setTextColor(71, 85, 105);
    
    // Calculate averages
    const temps = records.map(r => (r.temperature - 32) * 5/9);
    const hrs = records.map(r => r.heart_rate);
    const spo2s = records.map(r => r.oxygen_level);
    
    const avgTemp = (temps.reduce((a, b) => a + b, 0) / temps.length).toFixed(1);
    const avgHr = Math.round(hrs.reduce((a, b) => a + b, 0) / hrs.length);
    const avgSpo2 = Math.round(spo2s.reduce((a, b) => a + b, 0) / spo2s.length);
    
    const minTemp = Math.min(...temps).toFixed(1);
    const maxTemp = Math.max(...temps).toFixed(1);
    const minHr = Math.min(...hrs);
    const maxHr = Math.max(...hrs);
    const minSpo2 = Math.min(...spo2s);
    const maxSpo2 = Math.max(...spo2s);
    
    const summaryData = [
        ['Vital Sign', 'Average', 'Range', 'Status'],
        ['Temperature', `${avgTemp}°C`, `${minTemp}°C - ${maxTemp}°C`, getVitalStatus('temp', parseFloat(avgTemp))],
        ['Heart Rate', `${avgHr} bpm`, `${minHr} - ${maxHr} bpm`, getVitalStatus('hr', avgHr)],
        ['Oxygen Level', `${avgSpo2}%`, `${minSpo2}% - ${maxSpo2}%`, getVitalStatus('spo2', avgSpo2)]
    ];
    
    // Draw table
    const startY = yPos + 10;
    const cellHeight = 8;
    const colWidths = [50, 30, 40, 30];
    let currentY = startY;
    
    summaryData.forEach((row, rowIndex) => {
        let currentX = 25;
        
        row.forEach((cell, colIndex) => {
            // Header row
            if (rowIndex === 0) {
                doc.setFillColor(239, 246, 255);
                doc.rect(currentX, currentY, colWidths[colIndex], cellHeight, 'F');
                doc.setFont(undefined, 'bold');
                doc.setTextColor(14, 165, 233);
            } else {
                doc.setFont(undefined, 'normal');
                doc.setTextColor(71, 85, 105);
                
                // Alternate row colors
                if (rowIndex % 2 === 0) {
                    doc.setFillColor(248, 250, 252);
                    doc.rect(currentX, currentY, colWidths[colIndex], cellHeight, 'F');
                }
            }
            
            // Border
            doc.setDrawColor(226, 232, 240);
            doc.rect(currentX, currentY, colWidths[colIndex], cellHeight);
            
            // Text
            doc.text(cell, currentX + 2, currentY + 5.5);
            
            currentX += colWidths[colIndex];
        });
        
        currentY += cellHeight;
    });
    
    // Add note
    doc.setFontSize(9);
    doc.setTextColor(100, 116, 139);
    doc.text(`Total records analyzed: ${records.length}`, 25, currentY + 8);
    doc.text(`Data period: ${new Date(records[records.length - 1].timestamp).toLocaleDateString()} - ${new Date(records[0].timestamp).toLocaleDateString()}`, 25, currentY + 13);
}

/**
 * Get vital status
 */
function getVitalStatus(type, value) {
    if (type === 'temp') {
        if (value >= 36.5 && value <= 37.5) return 'Normal';
        if (value > 37.5 && value < 38) return 'Elevated';
        return 'Abnormal';
    } else if (type === 'hr') {
        if (value >= 60 && value <= 100) return 'Normal';
        if (value > 100 && value < 120) return 'Elevated';
        return 'Abnormal';
    } else if (type === 'spo2') {
        if (value >= 95) return 'Normal';
        if (value >= 90) return 'Low';
        return 'Critical';
    }
}

/**
 * Add report footer
 */
function addReportFooter(doc) {
    const pageCount = doc.internal.getNumberOfPages();
    
    for (let i = 1; i <= pageCount; i++) {
        doc.setPage(i);
        
        // Footer line
        doc.setDrawColor(226, 232, 240);
        doc.setLineWidth(0.5);
        doc.line(20, 280, 190, 280);
        
        // Footer text
        doc.setFontSize(9);
        doc.setTextColor(148, 163, 184);
        doc.text('Beat Suite AI - Automated Healthcare Monitoring System', 105, 285, { align: 'center' });
        doc.text(`Page ${i} of ${pageCount}`, 105, 290, { align: 'center' });
        doc.text('This is a computer-generated report', 105, 295, { align: 'center' });
    }
}

/**
 * Add AI Executive Summary
 */
function addAIExecutiveSummary(doc, aiReport, yPos) {
    doc.setFontSize(14);
    doc.setFont(undefined, 'bold');
    doc.setTextColor(139, 92, 246); // Purple for AI sections
    doc.text('🤖 AI HEALTH SUMMARY', 20, yPos);
    
    doc.setFontSize(10);
    doc.setFont(undefined, 'normal');
    doc.setTextColor(71, 85, 105);
    
    // Word wrap the executive summary
    const lines = doc.splitTextToSize(aiReport.executive_summary, 170);
    doc.text(lines, 20, yPos + 8);
    
    return yPos + 8 + (lines.length * 5);
}

/**
 * Add AI Vital Signs Analysis
 */
function addAIVitalAnalysis(doc, aiReport, yPos) {
    // Check if we need a new page
    if (yPos > 240) {
        doc.addPage();
        yPos = 20;
    }
    
    doc.setFontSize(14);
    doc.setFont(undefined, 'bold');
    doc.setTextColor(139, 92, 246);
    doc.text('🤖 AI VITAL SIGNS ANALYSIS', 20, yPos);
    
    doc.setFontSize(10);
    doc.setFont(undefined, 'normal');
    doc.setTextColor(71, 85, 105);
    
    const lines = doc.splitTextToSize(aiReport.vital_signs_analysis, 170);
    doc.text(lines, 20, yPos + 8);
    
    return yPos + 8 + (lines.length * 5);
}

/**
 * Add AI Health Trends
 */
function addAIHealthTrends(doc, aiReport, yPos) {
    // Check if we need a new page
    if (yPos > 240) {
        doc.addPage();
        yPos = 20;
    }
    
    doc.setFontSize(14);
    doc.setFont(undefined, 'bold');
    doc.setTextColor(139, 92, 246);
    doc.text('🤖 AI HEALTH TRENDS', 20, yPos);
    
    doc.setFontSize(10);
    doc.setFont(undefined, 'normal');
    doc.setTextColor(71, 85, 105);
    
    const lines = doc.splitTextToSize(aiReport.health_trends, 170);
    doc.text(lines, 20, yPos + 8);
    
    return yPos + 8 + (lines.length * 5);
}

/**
 * Add Comprehensive AI Analysis (new page)
 */
function addAIComprehensiveAnalysis(doc, aiReport, yPos) {
    // Title
    doc.setFontSize(16);
    doc.setFont(undefined, 'bold');
    doc.setTextColor(139, 92, 246);
    doc.text('🤖 COMPREHENSIVE AI HEALTH ANALYSIS', 20, yPos);
    doc.setTextColor(100, 116, 139);
    doc.setFontSize(9);
    doc.text(`Powered by Gemini AI • Confidence: ${aiReport.confidence_score}%`, 20, yPos + 6);
    
    yPos += 15;
    
    // Add AI Complete Analysis Report (1-3 paragraphs)
    yPos = addCompleteAIReport(doc, aiReport, yPos);
    yPos += 12;
    
    // Detected Concerns
    if (aiReport.detected_concerns && aiReport.detected_concerns.length > 0) {
        yPos = addAISection(doc, '⚠️ Detected Concerns', aiReport.detected_concerns, yPos, [239, 68, 68]);
        yPos += 8;
    }
    
    // Positive Indicators
    if (aiReport.positive_indicators && aiReport.positive_indicators.length > 0) {
        yPos = addAISection(doc, '✅ Positive Indicators', aiReport.positive_indicators, yPos, [16, 185, 129]);
        yPos += 8;
    }
    
    // Sleep & Recovery
    if (aiReport.sleep_recovery) {
        yPos = addAIParagraph(doc, '😴 Sleep & Recovery Analysis', aiReport.sleep_recovery, yPos);
        yPos += 8;
    }
    
    // Clinical Recommendations
    if (aiReport.clinical_recommendations && aiReport.clinical_recommendations.length > 0) {
        yPos = addAISection(doc, '💊 Clinical Recommendations', aiReport.clinical_recommendations, yPos, [59, 130, 246]);
        yPos += 8;
    }
    
    // Risk Assessment
    if (aiReport.risk_assessment) {
        yPos = addRiskAssessment(doc, aiReport.risk_assessment, yPos);
        yPos += 8;
    }
    
    // Prognosis
    if (aiReport.prognosis) {
        yPos = addAIParagraph(doc, '📈 Prognosis', aiReport.prognosis, yPos);
        yPos += 8;
    }
    
    // AI Effectiveness
    if (aiReport.ai_effectiveness) {
        yPos = addAIParagraph(doc, '🎯 AI System Effectiveness', aiReport.ai_effectiveness, yPos);
    }
    
    return yPos;
}

/**
 * Add Complete AI Analysis Report (1-3 paragraphs)
 */
function addCompleteAIReport(doc, aiReport, yPos) {
    console.log('🔍 addCompleteAIReport called with:', aiReport);
    
    try {
        // Section header
        doc.setFontSize(13);
        doc.setFont(undefined, 'bold');
        doc.setTextColor(30, 41, 59);
        doc.text('📋 Complete Medical Analysis Report', 20, yPos);
        
        yPos += 8;
        
        // Create comprehensive narrative by combining all AI insights
        const narrativeParagraphs = [];
    
    // Paragraph 1: Overall Assessment & Current Status
    let paragraph1 = `Based on comprehensive analysis of the patient's current vital signs and historical health data, `;
    paragraph1 += aiReport.executive_summary + ` `;
    paragraph1 += aiReport.vital_signs_analysis;
    narrativeParagraphs.push(paragraph1);
    
    // Paragraph 2: Trends & Patterns
    if (aiReport.health_trends) {
        let paragraph2 = `Longitudinal analysis reveals important trends in the patient's health trajectory. `;
        paragraph2 += aiReport.health_trends + ` `;
        
        // Add concern context if available
        if (aiReport.detected_concerns && aiReport.detected_concerns.length > 0) {
            paragraph2 += `Key areas requiring attention include: `;
            paragraph2 += aiReport.detected_concerns.slice(0, 2).join(', ');
            if (aiReport.detected_concerns.length > 2) {
                paragraph2 += `, and ${aiReport.detected_concerns.length - 2} additional factor${aiReport.detected_concerns.length - 2 > 1 ? 's' : ''}`;
            }
            paragraph2 += `. `;
        }
        
        // Add positive indicators
        if (aiReport.positive_indicators && aiReport.positive_indicators.length > 0) {
            paragraph2 += `Encouragingly, the patient demonstrates positive indicators including `;
            paragraph2 += aiReport.positive_indicators.slice(0, 2).join(' and ').toLowerCase() + `.`;
        }
        
        narrativeParagraphs.push(paragraph2);
    }
    
    // Paragraph 3: Clinical Recommendations & Prognosis
    let paragraph3 = ``;
    if (aiReport.sleep_recovery) {
        paragraph3 += aiReport.sleep_recovery + ` `;
    }
    
    if (aiReport.prognosis) {
        paragraph3 += aiReport.prognosis + ` `;
    }
    
    if (aiReport.clinical_recommendations && aiReport.clinical_recommendations.length > 0) {
        paragraph3 += `The AI system recommends the following clinical actions: `;
        paragraph3 += aiReport.clinical_recommendations.slice(0, 3).join('; ') + `.`;
    }
    
    if (paragraph3) {
        narrativeParagraphs.push(paragraph3);
    }
    
    // Render paragraphs with proper formatting
    doc.setFontSize(10);
    doc.setFont(undefined, 'normal');
    doc.setTextColor(51, 65, 85);
    doc.setLineHeightFactor(1.6);
    
    narrativeParagraphs.forEach((paragraph, index) => {
        // Check if we need a new page
        if (yPos > 240) {
            doc.addPage();
            yPos = 20;
        }
        
        // Add paragraph with proper text wrapping
        const lines = doc.splitTextToSize(paragraph, 170);
        doc.text(lines, 20, yPos);
        
        // Calculate height and add spacing between paragraphs
        const paragraphHeight = lines.length * 5;
        yPos += paragraphHeight;
        
        // Add spacing between paragraphs (except after last one)
        if (index < narrativeParagraphs.length - 1) {
            yPos += 6;
        }
    });
    
    // Add AI confidence note
    doc.setFontSize(9);
    doc.setTextColor(100, 116, 139);
    doc.setFont(undefined, 'italic');
    yPos += 8;
    doc.text(`Note: This analysis was generated using advanced AI algorithms with ${aiReport.confidence_score}% confidence based on available medical data.`, 20, yPos, { maxWidth: 170 });
    yPos += 8;
    
    // Add divider line
    doc.setDrawColor(226, 232, 240);
    doc.setLineWidth(0.5);
    doc.line(20, yPos, 190, yPos);
    yPos += 2;
    
    console.log('✅ Complete AI Report section added successfully');
    
    return yPos;
    
    } catch (error) {
        console.error('❌ Error in addCompleteAIReport:', error);
        // Add error message to PDF
        doc.setFontSize(10);
        doc.setTextColor(239, 68, 68);
        doc.text('Error generating complete AI report. Please see console for details.', 20, yPos);
        return yPos + 10;
    }
}

/**
 * Add AI section with bullet points
 */
function addAISection(doc, title, items, yPos, color = [139, 92, 246]) {
    // Check if we need a new page
    if (yPos > 240) {
        doc.addPage();
        yPos = 20;
    }
    
    doc.setFontSize(12);
    doc.setFont(undefined, 'bold');
    doc.setTextColor(...color);
    doc.text(title, 20, yPos);
    
    doc.setFontSize(10);
    doc.setFont(undefined, 'normal');
    doc.setTextColor(71, 85, 105);
    
    yPos += 6;
    
    items.forEach((item, index) => {
        if (yPos > 270) {
            doc.addPage();
            yPos = 20;
        }
        
        const lines = doc.splitTextToSize(`• ${item}`, 165);
        doc.text(lines, 25, yPos);
        yPos += lines.length * 5;
    });
    
    return yPos;
}

/**
 * Add AI paragraph section
 */
function addAIParagraph(doc, title, text, yPos) {
    // Check if we need a new page
    if (yPos > 240) {
        doc.addPage();
        yPos = 20;
    }
    
    doc.setFontSize(12);
    doc.setFont(undefined, 'bold');
    doc.setTextColor(139, 92, 246);
    doc.text(title, 20, yPos);
    
    doc.setFontSize(10);
    doc.setFont(undefined, 'normal');
    doc.setTextColor(71, 85, 105);
    
    const lines = doc.splitTextToSize(text, 170);
    doc.text(lines, 20, yPos + 6);
    
    return yPos + 6 + (lines.length * 5);
}

/**
 * Add Risk Assessment box
 */
function addRiskAssessment(doc, risk, yPos) {
    // Check if we need a new page
    if (yPos > 230) {
        doc.addPage();
        yPos = 20;
    }
    
    doc.setFontSize(12);
    doc.setFont(undefined, 'bold');
    doc.setTextColor(139, 92, 246);
    doc.text('⚕️ Risk Assessment', 20, yPos);
    
    // Risk level with color coding
    const riskColors = {
        'Low': [16, 185, 129],
        'Medium': [255, 167, 38],
        'High': [239, 68, 68],
        'Critical': [153, 27, 27]
    };
    
    const levelColor = riskColors[risk.level] || [100, 116, 139];
    
    doc.setFontSize(11);
    doc.setFont(undefined, 'bold');
    doc.setTextColor(...levelColor);
    doc.text(`Risk Level: ${risk.level}`, 25, yPos + 7);
    
    doc.setFontSize(10);
    doc.setFont(undefined, 'normal');
    doc.setTextColor(71, 85, 105);
    
    yPos += 13;
    
    // Risk factors
    if (risk.factors && risk.factors.length > 0) {
        doc.setFont(undefined, 'bold');
        doc.text('Risk Factors:', 25, yPos);
        doc.setFont(undefined, 'normal');
        yPos += 5;
        
        risk.factors.forEach(factor => {
            const lines = doc.splitTextToSize(`• ${factor}`, 165);
            doc.text(lines, 30, yPos);
            yPos += lines.length * 5;
        });
    }
    
    yPos += 3;
    
    // Mitigation strategies
    if (risk.mitigation && risk.mitigation.length > 0) {
        doc.setFont(undefined, 'bold');
        doc.text('Mitigation Strategies:', 25, yPos);
        doc.setFont(undefined, 'normal');
        yPos += 5;
        
        risk.mitigation.forEach(strategy => {
            const lines = doc.splitTextToSize(`• ${strategy}`, 165);
            doc.text(lines, 30, yPos);
            yPos += lines.length * 5;
        });
    }
    
    return yPos;
}

/**
 * Show loading indicator
 */
function showReportLoading(message = 'Generating patient report...') {
    const overlay = document.createElement('div');
    overlay.id = 'report-loading-overlay';
    overlay.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(15, 23, 42, 0.8);
        backdrop-filter: blur(8px);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 10000;
    `;
    
    overlay.innerHTML = `
        <div style="
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(20px);
            padding: 40px;
            border-radius: 20px;
            text-align: center;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
        ">
            <div style="
                width: 60px;
                height: 60px;
                margin: 0 auto 20px;
                border: 4px solid #E0F2FE;
                border-top: 4px solid #0EA5E9;
                border-radius: 50%;
                animation: spin 1s linear infinite;
            "></div>
            <div style="
                font-size: 16px;
                font-weight: 600;
                color: #1E293B;
                margin-bottom: 8px;
            ">Generating Report...</div>
            <div style="
                font-size: 13px;
                color: #64748B;
            ">${message}</div>
        </div>
    `;
    
    document.body.appendChild(overlay);
}

/**
 * Hide loading indicator
 */
function hideReportLoading() {
    const overlay = document.getElementById('report-loading-overlay');
    if (overlay) {
        overlay.remove();
    }
}

/**
 * Show notification
 */
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 80px;
        right: 20px;
        background: ${type === 'success' ? 'linear-gradient(135deg, #10B981 0%, #14B8A6 100%)' : 'linear-gradient(135deg, #EF4444 0%, #DC2626 100%)'};
        color: white;
        padding: 16px 24px;
        border-radius: 12px;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
        z-index: 10001;
        font-size: 14px;
        font-weight: 600;
        animation: slideInRight 0.3s ease;
        backdrop-filter: blur(10px);
    `;
    
    notification.textContent = message;
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideOutRight 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Add CSS animations safely
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', addReportStyles);
} else {
    addReportStyles();
}

function addReportStyles() {
    // Check if styles already added
    if (document.getElementById('report-generator-styles')) {
        return;
    }
    
    const style = document.createElement('style');
    style.id = 'report-generator-styles';
    style.textContent = `
        @keyframes spin {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
        }
        @keyframes slideInRight {
            from {
                transform: translateX(400px);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }
        @keyframes slideOutRight {
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
}
