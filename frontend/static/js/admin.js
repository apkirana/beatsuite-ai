/**
 * Admin Management JavaScript
 * Handles CRUD operations for patients, rooms, and users
 */

// Check authentication and admin role
window.addEventListener('DOMContentLoaded', () => {
    if (!window.authUtils.isAuthenticated()) {
        window.location.href = '/login';
        return;
    }
    
    const currentUser = window.authUtils.getCurrentUser();
    if (currentUser.role !== 'admin') {
        alert('Access denied. Admin privileges required.');
        window.location.href = '/dashboard';
        return;
    }
    
    // Load initial data
    loadPatients();
});

// Tab Management
function showTab(tabName) {
    // Hide all tabs
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    document.querySelectorAll('.tab-button').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Show selected tab
    document.getElementById(`${tabName}-tab`).classList.add('active');
    event.target.classList.add('active');
    
    // Load data
    if (tabName === 'patients') loadPatients();
    else if (tabName === 'rooms') loadRooms();
    else if (tabName === 'users') loadUsers();
}

// Navigation
function goToDashboard() {
    window.location.href = '/dashboard';
}

// Modal Management
function showModal(title, content) {
    document.getElementById('modalTitle').textContent = title;
    document.getElementById('modalBody').innerHTML = content;
    document.getElementById('formModal').classList.add('show');
}

function closeModal() {
    document.getElementById('formModal').classList.remove('show');
}

// ============= PATIENTS ============= //

async function loadPatients() {
    try {
        const response = await window.apiUtils.get('/api/patients');
        const data = await response.json();
        
        if (data.success) {
            displayPatients(data.patients);
        } else {
            alert('Error loading patients: ' + data.error);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to load patients');
    }
}

function displayPatients(patients) {
    const container = document.getElementById('patients-list');
    
    if (patients.length === 0) {
        container.innerHTML = '<p style="text-align: center; color: #999;">No patients found</p>';
        return;
    }
    
    container.innerHTML = patients.map(patient => `
        <div class="data-card">
            <div class="card-header">
                <div class="card-title">${patient.patient_name} (${patient.patient_id})</div>
                <div class="card-actions">
                    <button class="btn-edit" onclick='editPatient(${JSON.stringify(patient)})'>Edit</button>
                    <button class="btn-delete" onclick="deletePatient('${patient.patient_id}')">Delete</button>
                </div>
            </div>
            <div class="card-body">
                <div class="card-field">
                    <span class="field-label">Age</span>
                    <span class="field-value">${patient.age} years</span>
                </div>
                <div class="card-field">
                    <span class="field-label">Gender</span>
                    <span class="field-value">${patient.gender}</span>
                </div>
                <div class="card-field">
                    <span class="field-label">Diagnosis</span>
                    <span class="field-value">${patient.diagnosis}</span>
                </div>
                <div class="card-field">
                    <span class="field-label">Room</span>
                    <span class="field-value">${patient.room_id || 'Not assigned'}</span>
                </div>
                <div class="card-field">
                    <span class="field-label">Blood Type</span>
                    <span class="field-value">${patient.blood_type || 'N/A'}</span>
                </div>
                <div class="card-field">
                    <span class="field-label">Emergency Contact</span>
                    <span class="field-value">${patient.emergency_contact?.name || 'N/A'} (${patient.emergency_contact?.phone || 'N/A'})</span>
                </div>
            </div>
        </div>
    `).join('');
}

function showPatientForm(patient = null) {
    const isEdit = patient !== null;
    const formHTML = `
        <form onsubmit="submitPatientForm(event, ${isEdit})">
            <div class="form-group">
                <label>Patient Name *</label>
                <input type="text" name="patient_name" value="${patient?.patient_name || ''}" required>
            </div>
            <div class="form-group">
                <label>Age *</label>
                <input type="number" name="age" value="${patient?.age || ''}" min="0" required>
            </div>
            <div class="form-group">
                <label>Gender *</label>
                <select name="gender" required>
                    <option value="">Select...</option>
                    <option value="Male" ${patient?.gender === 'Male' ? 'selected' : ''}>Male</option>
                    <option value="Female" ${patient?.gender === 'Female' ? 'selected' : ''}>Female</option>
                    <option value="Other" ${patient?.gender === 'Other' ? 'selected' : ''}>Other</option>
                </select>
            </div>
            <div class="form-group">
                <label>Diagnosis *</label>
                <input type="text" name="diagnosis" value="${patient?.diagnosis || ''}" required>
            </div>
            <div class="form-group">
                <label>Admission Date</label>
                <input type="date" name="admission_date" value="${patient?.admission_date || ''}">
            </div>
            <div class="form-group">
                <label>Room ID</label>
                <input type="text" name="room_id" value="${patient?.room_id || ''}" placeholder="e.g., room_101">
            </div>
            <div class="form-group">
                <label>Blood Type</label>
                <input type="text" name="blood_type" value="${patient?.blood_type || ''}" placeholder="e.g., O+">
            </div>
            <div class="form-group">
                <label>Allergies</label>
                <textarea name="allergies">${patient?.allergies || ''}</textarea>
            </div>
            <div class="form-group">
                <label>Medical History</label>
                <textarea name="medical_history">${patient?.medical_history || ''}</textarea>
            </div>
            <div class="form-group">
                <label>Emergency Contact Name</label>
                <input type="text" name="emergency_name" value="${patient?.emergency_contact?.name || ''}">
            </div>
            <div class="form-group">
                <label>Emergency Contact Relation</label>
                <input type="text" name="emergency_relation" value="${patient?.emergency_contact?.relation || ''}">
            </div>
            <div class="form-group">
                <label>Emergency Contact Phone</label>
                <input type="tel" name="emergency_phone" value="${patient?.emergency_contact?.phone || ''}">
            </div>
            <input type="hidden" name="patient_id" value="${patient?.patient_id || ''}">
            <div class="form-actions">
                <button type="button" class="btn-cancel" onclick="closeModal()">Cancel</button>
                <button type="submit" class="btn-submit">${isEdit ? 'Update' : 'Create'} Patient</button>
            </div>
        </form>
    `;
    
    showModal(isEdit ? 'Edit Patient' : 'Add New Patient', formHTML);
}

function editPatient(patient) {
    showPatientForm(patient);
}

async function submitPatientForm(event, isEdit) {
    event.preventDefault();
    const formData = new FormData(event.target);
    const data = {
        patient_name: formData.get('patient_name'),
        age: parseInt(formData.get('age')),
        gender: formData.get('gender'),
        diagnosis: formData.get('diagnosis'),
        admission_date: formData.get('admission_date'),
        room_id: formData.get('room_id'),
        blood_type: formData.get('blood_type'),
        allergies: formData.get('allergies'),
        medical_history: formData.get('medical_history'),
        emergency_contact: {
            name: formData.get('emergency_name'),
            relation: formData.get('emergency_relation'),
            phone: formData.get('emergency_phone')
        }
    };
    
    try {
        let response;
        if (isEdit) {
            const patientId = formData.get('patient_id');
            response = await window.apiUtils.put(`/api/patients/${patientId}`, data);
        } else {
            response = await window.apiUtils.post('/api/patients', data);
        }
        
        const result = await response.json();
        
        if (result.success) {
            alert(result.message);
            closeModal();
            loadPatients();
        } else {
            alert('Error: ' + result.error);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to save patient');
    }
}

async function deletePatient(patientId) {
    if (!confirm('Are you sure you want to delete this patient?')) return;
    
    try {
        const response = await window.apiUtils.delete(`/api/patients/${patientId}`);
        const result = await response.json();
        
        if (result.success) {
            alert(result.message);
            loadPatients();
        } else {
            alert('Error: ' + result.error);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to delete patient');
    }
}

// ============= ROOMS ============= //

async function loadRooms() {
    try {
        const response = await window.apiUtils.get('/api/rooms-manage');
        const data = await response.json();
        
        if (data.success) {
            displayRooms(data.rooms);
        } else {
            alert('Error loading rooms: ' + data.error);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to load rooms');
    }
}

function displayRooms(rooms) {
    const container = document.getElementById('rooms-list');
    
    if (rooms.length === 0) {
        container.innerHTML = '<p style="text-align: center; color: #999;">No rooms found</p>';
        return;
    }
    
    container.innerHTML = rooms.map(room => `
        <div class="data-card">
            <div class="card-header">
                <div class="card-title">Room ${room.room_number} (${room.room_id})</div>
                <div class="card-actions">
                    <button class="btn-edit" onclick='editRoom(${JSON.stringify(room)})'>Edit</button>
                    <button class="btn-delete" onclick="deleteRoom('${room.room_id}')">Delete</button>
                </div>
            </div>
            <div class="card-body">
                <div class="card-field">
                    <span class="field-label">Floor</span>
                    <span class="field-value">Floor ${room.floor}</span>
                </div>
                <div class="card-field">
                    <span class="field-label">Ward</span>
                    <span class="field-value">${room.ward}</span>
                </div>
                <div class="card-field">
                    <span class="field-label">Type</span>
                    <span class="field-value">${room.room_type}</span>
                </div>
                <div class="card-field">
                    <span class="field-label">Status</span>
                    <span class="status-badge status-${room.status}">${room.status}</span>
                </div>
                <div class="card-field">
                    <span class="field-label">Patient</span>
                    <span class="field-value">${room.patient_id || 'None'}</span>
                </div>
                <div class="card-field">
                    <span class="field-label">AI Control</span>
                    <button 
                        class="btn-edit" 
                        onclick="toggleRoomAI('${room.room_id}', ${room.ai_is_active || false})"
                        style="padding: 6px 14px; font-size: 11px; ${room.ai_is_active ? 'background: rgba(239, 68, 68, 0.1); color: var(--danger); border-color: rgba(239, 68, 68, 0.3);' : 'background: rgba(16, 185, 129, 0.1); color: #10B981; border-color: rgba(16, 185, 129, 0.3);'}">
                        ${room.ai_is_active ? '⏸️ Pause AI' : '▶️ Activate AI'}
                    </button>
                </div>
            </div>
        </div>
    `).join('');
}

function showRoomForm(room = null) {
    const isEdit = room !== null;
    const formHTML = `
        <form onsubmit="submitRoomForm(event, ${isEdit})">
            <div class="form-group">
                <label>Room Number *</label>
                <input type="text" name="room_number" value="${room?.room_number || ''}" required>
            </div>
            <div class="form-group">
                <label>Floor *</label>
                <input type="number" name="floor" value="${room?.floor || ''}" min="1" required>
            </div>
            <div class="form-group">
                <label>Ward *</label>
                <input type="text" name="ward" value="${room?.ward || ''}" required>
            </div>
            <div class="form-group">
                <label>Room Type *</label>
                <select name="room_type" required>
                    <option value="">Select...</option>
                    <option value="Private" ${room?.room_type === 'Private' ? 'selected' : ''}>Private</option>
                    <option value="Shared" ${room?.room_type === 'Shared' ? 'selected' : ''}>Shared</option>
                    <option value="ICU" ${room?.room_type === 'ICU' ? 'selected' : ''}>ICU</option>
                </select>
            </div>
            <div class="form-group">
                <label>Status *</label>
                <select name="status" required>
                    <option value="">Select...</option>
                    <option value="available" ${room?.status === 'available' ? 'selected' : ''}>Available</option>
                    <option value="occupied" ${room?.status === 'occupied' ? 'selected' : ''}>Occupied</option>
                    <option value="maintenance" ${room?.status === 'maintenance' ? 'selected' : ''}>Maintenance</option>
                </select>
            </div>
            <div class="form-group">
                <label>Patient ID</label>
                <input type="text" name="patient_id" value="${room?.patient_id || ''}" placeholder="e.g., P001">
            </div>
            <input type="hidden" name="room_id" value="${room?.room_id || ''}">
            <div class="form-actions">
                <button type="button" class="btn-cancel" onclick="closeModal()">Cancel</button>
                <button type="submit" class="btn-submit">${isEdit ? 'Update' : 'Create'} Room</button>
            </div>
        </form>
    `;
    
    showModal(isEdit ? 'Edit Room' : 'Add New Room', formHTML);
}

function editRoom(room) {
    showRoomForm(room);
}

async function submitRoomForm(event, isEdit) {
    event.preventDefault();
    const formData = new FormData(event.target);
    const data = {
        room_number: formData.get('room_number'),
        floor: parseInt(formData.get('floor')),
        ward: formData.get('ward'),
        room_type: formData.get('room_type'),
        status: formData.get('status'),
        patient_id: formData.get('patient_id') || null
    };
    
    try {
        let response;
        if (isEdit) {
            const roomId = formData.get('room_id');
            response = await window.apiUtils.put(`/api/rooms-manage/${roomId}`, data);
        } else {
            response = await window.apiUtils.post('/api/rooms-manage', data);
        }
        
        const result = await response.json();
        
        if (result.success) {
            alert(result.message);
            closeModal();
            loadRooms();
        } else {
            alert('Error: ' + result.error);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to save room');
    }
}

async function deleteRoom(roomId) {
    if (!confirm('Are you sure you want to delete this room?')) return;
    
    try {
        const response = await window.apiUtils.delete(`/api/rooms-manage/${roomId}`);
        const result = await response.json();
        
        if (result.success) {
            alert(result.message);
            loadRooms();
        } else {
            alert('Error: ' + result.error);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to delete room');
    }
}

async function toggleRoomAI(roomId, isActive) {
    try {
        console.log(`[ADMIN] Toggle AI for ${roomId}: Currently ${isActive ? 'active' : 'inactive'}`);
        
        let response;
        
        if (isActive) {
            // Pause AI - set manual override
            response = await fetch(`/api/rooms/${roomId}/override`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                credentials: 'include',
                body: JSON.stringify({
                    brightness: 50,
                    volume: 30
                })
            });
        } else {
            // Resume AI control
            response = await fetch(`/api/rooms/${roomId}/resume`, {
                method: 'POST',
                credentials: 'include'
            });
        }
        
        const data = await response.json();
        
        if (data.success) {
            alert(data.message);
            loadRooms();  // Reload to update UI
        } else {
            alert('Failed: ' + (data.error || 'Unknown error'));
        }
        
    } catch (error) {
        console.error('Error toggling AI:', error);
        alert('Failed to toggle AI control');
    }
}

// ============= USERS ============= //

async function loadUsers() {
    try {
        const response = await window.apiUtils.get('/api/users');
        const data = await response.json();
        
        if (data.success) {
            displayUsers(data.users);
        } else {
            alert('Error loading users: ' + data.error);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to load users');
    }
}

function displayUsers(users) {
    const container = document.getElementById('users-list');
    
    if (users.length === 0) {
        container.innerHTML = '<p style="text-align: center; color: #999;">No users found</p>';
        return;
    }
    
    container.innerHTML = users.map(user => `
        <div class="data-card">
            <div class="card-header">
                <div class="card-title">${user.full_name} (@${user.username})</div>
                <div class="card-actions">
                    <button class="btn-edit" onclick='editUser(${JSON.stringify(user)})'>Edit</button>
                    <button class="btn-delete" onclick="deleteUser('${user.user_id}')">Delete</button>
                </div>
            </div>
            <div class="card-body">
                <div class="card-field">
                    <span class="field-label">Role</span>
                    <span class="status-badge role-${user.role}">${user.role}</span>
                </div>
                <div class="card-field">
                    <span class="field-label">Email</span>
                    <span class="field-value">${user.email}</span>
                </div>
                <div class="card-field">
                    <span class="field-label">Phone</span>
                    <span class="field-value">${user.phone || 'N/A'}</span>
                </div>
                <div class="card-field">
                    <span class="field-label">User ID</span>
                    <span class="field-value">${user.user_id}</span>
                </div>
            </div>
        </div>
    `).join('');
}

function showUserForm(user = null) {
    const isEdit = user !== null;
    const formHTML = `
        <form onsubmit="submitUserForm(event, ${isEdit})">
            <div class="form-group">
                <label>Full Name *</label>
                <input type="text" name="full_name" value="${user?.full_name || ''}" required>
            </div>
            <div class="form-group">
                <label>Username *</label>
                <input type="text" name="username" value="${user?.username || ''}" ${isEdit ? 'readonly' : ''} required>
            </div>
            <div class="form-group">
                <label>Password ${isEdit ? '(leave blank to keep current)' : '*'}</label>
                <input type="password" name="password" ${isEdit ? '' : 'required'}>
            </div>
            <div class="form-group">
                <label>Role *</label>
                <select name="role" required>
                    <option value="">Select...</option>
                    <option value="admin" ${user?.role === 'admin' ? 'selected' : ''}>Admin</option>
                    <option value="nurse" ${user?.role === 'nurse' ? 'selected' : ''}>Nurse</option>
                    <option value="family" ${user?.role === 'family' ? 'selected' : ''}>Family</option>
                </select>
            </div>
            <div class="form-group">
                <label>Email *</label>
                <input type="email" name="email" value="${user?.email || ''}" required>
            </div>
            <div class="form-group">
                <label>Phone</label>
                <input type="tel" name="phone" value="${user?.phone || ''}">
            </div>
            <input type="hidden" name="user_id" value="${user?.user_id || ''}">
            <div class="form-actions">
                <button type="button" class="btn-cancel" onclick="closeModal()">Cancel</button>
                <button type="submit" class="btn-submit">${isEdit ? 'Update' : 'Create'} User</button>
            </div>
        </form>
    `;
    
    showModal(isEdit ? 'Edit User' : 'Add New User', formHTML);
}

function editUser(user) {
    showUserForm(user);
}

async function submitUserForm(event, isEdit) {
    event.preventDefault();
    const formData = new FormData(event.target);
    const data = {
        full_name: formData.get('full_name'),
        username: formData.get('username'),
        role: formData.get('role'),
        email: formData.get('email'),
        phone: formData.get('phone')
    };
    
    // Only include password if provided
    const password = formData.get('password');
    if (password) {
        data.password = password;
    }
    
    try {
        let response;
        if (isEdit) {
            const userId = formData.get('user_id');
            response = await window.apiUtils.put(`/api/users/${userId}`, data);
        } else {
            response = await window.apiUtils.post('/api/users', data);
        }
        
        const result = await response.json();
        
        if (result.success) {
            alert(result.message);
            closeModal();
            loadUsers();
        } else {
            alert('Error: ' + result.error);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to save user');
    }
}

async function deleteUser(userId) {
    if (!confirm('Are you sure you want to delete this user?')) return;
    
    try {
        const response = await window.apiUtils.delete(`/api/users/${userId}`);
        const result = await response.json();
        
        if (result.success) {
            alert(result.message);
            loadUsers();
        } else {
            alert('Error: ' + result.error);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to delete user');
    }
}
