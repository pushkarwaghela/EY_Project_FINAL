// static/js/qr-scanner.js - COMPLETE QR SCANNER SCRIPT

// ========== GLOBAL VARIABLES ==========
let qrScanner = null;
let currentCameraId = null;
let isFlashOn = false;
let isScannerActive = false;

// ========== INITIALIZATION ==========
document.addEventListener('DOMContentLoaded', function() {
    console.log('QR Scanner script loaded');
    
    // Initialize when page loads
    initializePage();
});

function initializePage() {
    // Set up modal events
    const scannerModal = document.getElementById('qrScannerModal');
    if (scannerModal) {
        scannerModal.addEventListener('shown.bs.modal', function() {
            console.log('Scanner modal shown');
            initializeScanner();
            loadCameras();
        });
        
        scannerModal.addEventListener('hidden.bs.modal', function() {
            console.log('Scanner modal hidden');
            stopScanner();
        });
    }
    
    // Update Scan button
    const scanBtn = document.querySelector('[data-action="scan-qr"]');
    if (scanBtn) {
        scanBtn.addEventListener('click', openScannerWithChecks);
        scanBtn.removeAttribute('data-bs-toggle');
        scanBtn.removeAttribute('data-bs-target');
    }
    
    // Add event listeners to modal buttons
    document.getElementById('start-btn')?.addEventListener('click', startScanner);
    document.getElementById('stop-btn')?.addEventListener('click', stopScanner);
    document.getElementById('flash-btn')?.addEventListener('click', toggleFlash);
}

// ========== MAIN FUNCTIONS ==========

async function openScannerWithChecks(event) {
    event.preventDefault();
    console.log('Opening scanner with checks...');
    
    try {
        // Check for mediaDevices support
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            showToast('Your browser does not support camera access. Please use Chrome, Firefox, or Edge.', 'error');
            return;
        }
        
        // Open the modal
        const modalElement = document.getElementById('qrScannerModal');
        if (!modalElement) {
            showToast('Scanner modal not found', 'error');
            return;
        }
        
        const modal = new bootstrap.Modal(modalElement);
        modal.show();
        
    } catch (error) {
        console.error('Camera check error:', error);
        showToast('Error: ' + error.message, 'error');
    }
}

async function initializeScanner() {
    console.log('Initializing scanner...');
    
    try {
        // Test camera access
        const stream = await navigator.mediaDevices.getUserMedia({ 
            video: { facingMode: 'environment' } 
        });
        
        // Stop the test stream
        stream.getTracks().forEach(track => track.stop());
        
        // Initialize scanner
        qrScanner = new Html5Qrcode("qr-reader");
        
        console.log('Scanner initialized successfully');
        showToast('Camera ready! Click Start to begin scanning.', 'success');
        
    } catch (error) {
        console.error('Camera initialization error:', error);
        showToast('Camera error: ' + error.message, 'error');
    }
}

async function loadCameras() {
    try {
        const devices = await navigator.mediaDevices.enumerateDevices();
        const videoDevices = devices.filter(device => device.kind === 'videoinput');
        const cameraSelect = document.getElementById('camera-select');
        
        if (!cameraSelect) return;
        
        cameraSelect.innerHTML = '<option value="">Auto-select (Recommended)</option>';
        
        videoDevices.forEach((device, index) => {
            const option = document.createElement('option');
            option.value = device.deviceId;
            option.text = device.label || `Camera ${index + 1}`;
            cameraSelect.appendChild(option);
        });
        
        cameraSelect.addEventListener('change', function() {
            currentCameraId = this.value;
            console.log('Camera selected:', currentCameraId);
            if (qrScanner && isScannerActive) {
                stopScanner();
                setTimeout(() => startScanner(), 500);
            }
        });
        
    } catch (error) {
        console.error('Error loading cameras:', error);
    }
}

async function startScanner() {
    console.log('Starting scanner...');
    
    if (!qrScanner) {
        showToast('Scanner not initialized. Please wait...', 'error');
        return;
    }
    
    try {
        const qrCodeSuccessCallback = (decodedText, decodedResult) => {
            console.log('QR Code scanned:', decodedText);
            stopScanner();
            processScannedQR(decodedText);
        };
        
        const qrCodeErrorCallback = (error) => {
            // Ignore common errors
            if (!error.includes('NotFoundException') && !error.includes('NoMultiFormatReader')) {
                console.log('QR Scan Error:', error);
            }
        };
        
        const config = {
            fps: 10,
            qrbox: { width: 250, height: 250 },
            aspectRatio: 1.0
        };
        
        let cameraConfig = currentCameraId ? 
            { deviceId: { exact: currentCameraId } } : 
            { facingMode: "environment" };
        
        await qrScanner.start(cameraConfig, config, qrCodeSuccessCallback, qrCodeErrorCallback);
        
        // Update UI
        isScannerActive = true;
        document.getElementById('start-btn')?.classList?.add('d-none');
        document.getElementById('stop-btn')?.classList?.remove('d-none');
        
        const scannerContainer = document.getElementById('scanner-container');
        if (scannerContainer) scannerContainer.style.border = '3px solid #28a745';
        
        showToast('Scanner started. Point camera at QR code...', 'info');
        
    } catch (error) {
        console.error('Scanner start error:', error);
        showToast('Failed to start scanner: ' + error.message, 'error');
    }
}

async function stopScanner() {
    console.log('Stopping scanner...');
    
    if (qrScanner && isScannerActive) {
        try {
            await qrScanner.stop();
            isScannerActive = false;
            
            document.getElementById('start-btn')?.classList?.remove('d-none');
            document.getElementById('stop-btn')?.classList?.add('d-none');
            
            const scannerContainer = document.getElementById('scanner-container');
            if (scannerContainer) scannerContainer.style.border = 'none';
            
            console.log('Scanner stopped');
            
        } catch (error) {
            console.error('Error stopping scanner:', error);
        }
    }
}

async function toggleFlash() {
    if (!qrScanner || !isScannerActive) return;
    
    try {
        const videoElement = document.querySelector('#qr-reader video');
        if (!videoElement) return;
        
        const track = videoElement.srcObject.getVideoTracks()[0];
        if (!track || !track.getCapabilities().torch) {
            showToast('Flash not supported', 'warning');
            return;
        }
        
        isFlashOn = !isFlashOn;
        await track.applyConstraints({ advanced: [{ torch: isFlashOn }] });
        
        const flashBtn = document.getElementById('flash-btn');
        if (flashBtn) {
            if (isFlashOn) {
                flashBtn.innerHTML = '<i class="fas fa-lightbulb text-warning"></i> Flash On';
                flashBtn.classList.remove('btn-outline-secondary');
                flashBtn.classList.add('btn-warning');
            } else {
                flashBtn.innerHTML = '<i class="fas fa-lightbulb"></i> Flash';
                flashBtn.classList.remove('btn-warning');
                flashBtn.classList.add('btn-outline-secondary');
            }
        }
        
    } catch (error) {
        console.error('Flash error:', error);
    }
}

function processScannedQR(qrData) {
    console.log('Processing QR:', qrData);
    
    const scannerContainer = document.getElementById('scanner-container');
    if (!scannerContainer) return;
    
    scannerContainer.innerHTML = `
        <div class="d-flex flex-column align-items-center justify-content-center h-100">
            <div class="spinner-border text-primary mb-3"></div>
            <h5>Processing...</h5>
        </div>
    `;
    
    fetch('/attendance/mark/qr/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({ qr_data: qrData })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            scannerContainer.innerHTML = `
                <div class="d-flex flex-column align-items-center justify-content-center h-100">
                    <i class="fas fa-check-circle fa-4x text-success mb-3"></i>
                    <h4 class="text-success">Success!</h4>
                    <p>${data.message}</p>
                </div>
            `;
            
            setTimeout(() => {
                const modal = bootstrap.Modal.getInstance(document.getElementById('qrScannerModal'));
                if (modal) modal.hide();
                setTimeout(() => location.reload(), 1000);
            }, 2000);
            
        } else {
            scannerContainer.innerHTML = `
                <div class="d-flex flex-column align-items-center justify-content-center h-100">
                    <i class="fas fa-exclamation-triangle fa-4x text-danger mb-3"></i>
                    <h4 class="text-danger">Error!</h4>
                    <p>${data.message}</p>
                    <button class="btn btn-primary mt-3" onclick="window.restartScanner()">
                        Scan Again
                    </button>
                </div>
            `;
        }
    })
    .catch(error => {
        console.error('Network error:', error);
        scannerContainer.innerHTML = `
            <div class="d-flex flex-column align-items-center justify-content-center h-100">
                <i class="fas fa-wifi-slash fa-4x text-danger mb-3"></i>
                <h4>Network Error</h4>
                <button class="btn btn-primary mt-3" onclick="window.restartScanner()">
                    Retry
                </button>
            </div>
        `;
    });
}

function restartScanner() {
    const scannerContainer = document.getElementById('scanner-container');
    if (!scannerContainer) return;
    
    scannerContainer.innerHTML = '<div id="qr-reader" style="width: 100%; height: 300px;"></div>';
    qrScanner = new Html5Qrcode("qr-reader");
    setTimeout(() => startScanner(), 500);
}

// Utility functions
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

function showToast(message, type = 'info') {
    // Simple alert for now - replace with your toast system
    alert(type.toUpperCase() + ': ' + message);
}

// Make functions globally available
window.openScannerWithChecks = openScannerWithChecks;
window.startScanner = startScanner;
window.stopScanner = stopScanner;
window.toggleFlash = toggleFlash;
window.restartScanner = restartScanner;
window.showToast = showToast;