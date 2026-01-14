// QR Scanner Implementation
class AttendanceScanner {
    constructor(options = {}) {
        this.scanner = null;
        this.videoElement = null;
        this.canvasElement = null;
        this.canvasContext = null;
        this.stream = null;
        this.isScanning = false;
        
        this.options = {
            containerId: 'scannerContainer',
            resultId: 'qrResult',
            onSuccess: null,
            onError: null,
            ...options
        };
        
        this.init();
    }
    
    init() {
        this.videoElement = document.createElement('video');
        this.canvasElement = document.createElement('canvas');
        this.canvasContext = this.canvasElement.getContext('2d');
        
        this.videoElement.style.width = '100%';
        this.videoElement.style.height = 'auto';
        this.videoElement.setAttribute('playsinline', 'true');
        
        const container = document.getElementById(this.options.containerId);
        if (container) {
            container.innerHTML = '';
            container.appendChild(this.videoElement);
        }
    }
    
    async start() {
        if (this.isScanning) return;
        
        try {
            this.stream = await navigator.mediaDevices.getUserMedia({
                video: {
                    facingMode: 'environment',
                    width: { ideal: 1280 },
                    height: { ideal: 720 }
                }
            });
            
            this.videoElement.srcObject = this.stream;
            await this.videoElement.play();
            
            this.isScanning = true;
            this.scanFrame();
            
            if (this.options.onSuccess) {
                this.options.onSuccess('Scanner started successfully');
            }
            
        } catch (error) {
            console.error('Error accessing camera:', error);
            if (this.options.onError) {
                this.options.onError('Failed to access camera. Please check permissions.');
            }
            this.showManualScanner();
        }
    }
    
    showManualScanner() {
        const container = document.getElementById(this.options.containerId);
        container.innerHTML = `
            <div class="alert alert-warning">
                <i class="fas fa-exclamation-triangle me-2"></i>
                Camera not available. Please use manual entry.
            </div>
            <div class="manual-input">
                <div class="mb-3">
                    <label class="form-label">Enter Event Code</label>
                    <input type="text" class="form-control" id="manualEventCode" 
                           placeholder="Enter event code from organizer">
                </div>
                <button class="btn btn-primary w-100" onclick="submitManualAttendance()">
                    <i class="fas fa-paper-plane me-2"></i>Submit Attendance
                </button>
            </div>
        `;
    }
    
    stop() {
        if (this.stream) {
            this.stream.getTracks().forEach(track => track.stop());
        }
        this.isScanning = false;
        this.scanner = null;
    }
    
    scanFrame() {
        if (!this.isScanning) return;
        
        if (this.videoElement.readyState === this.videoElement.HAVE_ENOUGH_DATA) {
            this.canvasElement.height = this.videoElement.videoHeight;
            this.canvasElement.width = this.videoElement.videoWidth;
            
            this.canvasContext.drawImage(
                this.videoElement,
                0, 0,
                this.canvasElement.width,
                this.canvasElement.height
            );
            
            const imageData = this.canvasContext.getImageData(
                0, 0,
                this.canvasElement.width,
                this.canvasElement.height
            );
            
            // Simple QR detection (you can integrate a proper QR library)
            const qrCode = this.detectQRCode(imageData);
            
            if (qrCode) {
                this.processQRCode(qrCode);
            }
        }
        
        requestAnimationFrame(() => this.scanFrame());
    }
    
    detectQRCode(imageData) {
        // This is a simplified detection
        // In production, use a library like jsQR or Instascan
        return null; // Placeholder
    }
    
    async processQRCode(qrData) {
        try {
            const response = await fetch('/attendance/mark/qr/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({ qr_data: qrData })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.stop();
                this.showSuccess(data);
            } else {
                this.showError(data.message);
            }
        } catch (error) {
            console.error('Error processing QR:', error);
            this.showError('Failed to process QR code');
        }
    }
    
    showSuccess(data) {
        const container = document.getElementById(this.options.containerId);
        container.innerHTML = `
            <div class="text-center py-4">
                <div class="success-icon mb-3">
                    <i class="fas fa-check-circle fa-4x text-success"></i>
                </div>
                <h4 class="text-success mb-3">Attendance Marked!</h4>
                <div class="card bg-success bg-opacity-10 border-success mb-3">
                    <div class="card-body">
                        <h5>${data.data.event}</h5>
                        <p class="mb-1">
                            <i class="fas fa-clock me-1"></i>
                            ${data.data.time} on ${data.data.date}
                        </p>
                        <small class="text-muted">Method: ${data.data.method}</small>
                    </div>
                </div>
                <button class="btn btn-outline-success" onclick="startScanner()">
                    <i class="fas fa-redo me-2"></i>Scan Again
                </button>
            </div>
        `;
    }
    
    showError(message) {
        const container = document.getElementById(this.options.containerId);
        const errorDiv = document.createElement('div');
        errorDiv.className = 'alert alert-danger alert-dismissible fade show';
        errorDiv.innerHTML = `
            <i class="fas fa-exclamation-circle me-2"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        // Add to container without clearing scanner
        container.prepend(errorDiv);
    }
}

// Global scanner instance
let attendanceScanner = null;

// Initialize scanner
function initScanner() {
    attendanceScanner = new AttendanceScanner({
        containerId: 'scannerContainer',
        resultId: 'qrResult',
        onSuccess: (message) => {
            console.log('Scanner:', message);
        },
        onError: (error) => {
            console.error('Scanner error:', error);
        }
    });
}

// Start scanner
function startScanner() {
    if (!attendanceScanner) {
        initScanner();
    }
    attendanceScanner.start();
}

// Stop scanner
function stopScanner() {
    if (attendanceScanner) {
        attendanceScanner.stop();
    }
}

// Manual attendance submission
async function submitManualAttendance() {
    const eventCode = document.getElementById('manualEventCode')?.value;
    
    if (!eventCode) {
        showToast('error', 'Please enter event code');
        return;
    }
    
    const response = await fetch('/attendance/mark/manual/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: new URLSearchParams({
            event_code: eventCode,
            student_id: '{{ user.student_id }}'
        })
    });
    
    if (response.ok) {
        showToast('success', 'Attendance marked successfully');
        setTimeout(() => location.reload(), 1500);
    } else {
        showToast('error', 'Failed to mark attendance');
    }
}

// Helper function to get CSRF token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Toast notification
function showToast(type, message) {
    const toastId = 'toast-' + Date.now();
    const toastHtml = `
        <div id="${toastId}" class="toast align-items-center text-bg-${type} border-0" role="alert">
            <div class="d-flex">
                <div class="toast-body">
                    <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-triangle'} me-2"></i>
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        </div>
    `;
    
    let toastContainer = document.querySelector('.toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        document.body.appendChild(toastContainer);
    }
    
    toastContainer.insertAdjacentHTML('beforeend', toastHtml);
    
    const toastEl = document.getElementById(toastId);
    const toast = new bootstrap.Toast(toastEl);
    toast.show();
    
    toastEl.addEventListener('hidden.bs.toast', function () {
        toastEl.remove();
    });
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', function() {
    // Initialize scanner if on attendance page
    if (document.getElementById('scannerContainer')) {
        initScanner();
    }
    
    // Auto-refresh attendance data
    if (document.getElementById('liveAttendance')) {
        setInterval(updateLiveAttendance, 30000);
        updateLiveAttendance();
    }
});

// Update live attendance data
async function updateLiveAttendance() {
    try {
        const response = await fetch('/attendance/live/');
        const data = await response.json();
        
        if (data.success) {
            // Update UI with live data
            const container = document.getElementById('liveAttendance');
            if (container) {
                container.innerHTML = data.attendance.map(record => `
                    <div class="list-group-item">
                        <div class="d-flex justify-content-between align-items-center">
                            <div>
                                <h6 class="mb-1">${record.student_name}</h6>
                                <small class="text-muted">${record.event}</small>
                            </div>
                            <span class="badge bg-${record.status_color}">
                                ${record.time}
                            </span>
                        </div>
                    </div>
                `).join('');
            }
        }
    } catch (error) {
        console.error('Error updating live attendance:', error);
    }
}