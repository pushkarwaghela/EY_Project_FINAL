// QR Scanner using HTML5-QRCode
class QRScanner {
    constructor(config = {}) {
        this.scanner = null;
        this.config = {
            containerId: 'qr-reader',
            onSuccess: null,
            onError: null,
            ...config
        };
        this.isScanning = false;
    }

    async start() {
        if (this.isScanning) return;
        
        try {
            // Clear previous scanner
            const container = document.getElementById(this.config.containerId);
            if (container) {
                container.innerHTML = '';
                
                // Create scanner UI
                container.innerHTML = `
                    <div class="scanner-viewport">
                        <video id="scanner-video" playsinline></video>
                        <div class="scanner-overlay">
                            <div class="scanner-frame"></div>
                            <div class="scanner-line"></div>
                        </div>
                    </div>
                `;
                
                // Initialize scanner using html5-qrcode
                if (typeof Html5QrcodeScanner !== 'undefined') {
                    this.scanner = new Html5QrcodeScanner(
                        this.config.containerId,
                        {
                            fps: 10,
                            qrbox: { width: 250, height: 250 },
                            rememberLastUsedCamera: true,
                            supportedScanTypes: [Html5QrcodeScanType.SCAN_TYPE_CAMERA]
                        }
                    );
                    
                    this.scanner.render(
                        (decodedText, decodedResult) => {
                            if (this.config.onSuccess) {
                                this.config.onSuccess(decodedText, decodedResult);
                            }
                        },
                        (errorMessage) => {
                            if (this.config.onError) {
                                this.config.onError(errorMessage);
                            }
                        }
                    );
                } else {
                    // Fallback to manual camera access
                    await this.startManualScanner();
                }
                
                this.isScanning = true;
                
            } catch (error) {
                console.error('Scanner error:', error);
                if (this.config.onError) {
                    this.config.onError('Failed to start scanner: ' + error.message);
                }
            }
        } catch (error) {
            console.error('Scanner error:', error);
            if (this.config.onError) {
                this.config.onError('Failed to start scanner: ' + error.message);
            }
        }
    }

    async startManualScanner() {
        const video = document.getElementById('scanner-video');
        
        try {
            const stream = await navigator.mediaDevices.getUserMedia({
                video: {
                    facingMode: 'environment',
                    width: { ideal: 1280 },
                    height: { ideal: 720 }
                }
            });
            
            video.srcObject = stream;
            await video.play();
            
            // Start scanning with jsQR library
            this.startQRDetection(video);
            
        } catch (error) {
            console.error('Camera error:', error);
            throw new Error('Camera access denied or not available');
        }
    }

    startQRDetection(video) {
        const canvas = document.createElement('canvas');
        const context = canvas.getContext('2d');
        
        const checkQRCode = () => {
            if (!this.isScanning) return;
            
            if (video.readyState === video.HAVE_ENOUGH_DATA) {
                canvas.width = video.videoWidth;
                canvas.height = video.videoHeight;
                context.drawImage(video, 0, 0, canvas.width, canvas.height);
                
                const imageData = context.getImageData(0, 0, canvas.width, canvas.height);
                
                // Check for QR code
                if (typeof jsQR === 'function') {
                    const code = jsQR(imageData.data, imageData.width, imageData.height, {
                        inversionAttempts: 'dontInvert',
                    });
                    
                    if (code) {
                        if (this.config.onSuccess) {
                            this.config.onSuccess(code.data, code);
                        }
                    }
                }
            }
            
            requestAnimationFrame(() => checkQRCode());
        };
        
        checkQRCode();
    }

    stop() {
        this.isScanning = false;
        
        if (this.scanner && this.scanner.clear) {
            this.scanner.clear();
        }
        
        // Stop all video streams
        const video = document.getElementById('scanner-video');
        if (video && video.srcObject) {
            video.srcObject.getTracks().forEach(track => track.stop());
        }
        
        this.scanner = null;
    }
}

// Global scanner instance
let attendanceScanner = null;

// Initialize scanner
function initQRScanner(onSuccess, onError) {
    attendanceScanner = new QRScanner({
        containerId: 'qr-reader',
        onSuccess: onSuccess,
        onError: onError
    });
}

// Start scanner
async function startQRScanner() {
    if (!attendanceScanner) {
        initQRScanner(
            (data) => processQRCode(data),
            (error) => showScannerError(error)
        );
    }
    
    try {
        await attendanceScanner.start();
        updateScannerUI(true);
    } catch (error) {
        showScannerError(error);
    }
}

// Stop scanner
function stopQRScanner() {
    if (attendanceScanner) {
        attendanceScanner.stop();
    }
    updateScannerUI(false);
}

// Update scanner UI
function updateScannerUI(isActive) {
    const startBtn = document.getElementById('startScannerBtn');
    const stopBtn = document.getElementById('stopScannerBtn');
    const placeholder = document.getElementById('scannerPlaceholder');
    const scannerView = document.getElementById('scannerView');
    
    if (isActive) {
        startBtn.style.display = 'none';
        stopBtn.style.display = 'inline-block';
        placeholder.style.display = 'none';
        scannerView.style.display = 'block';
        scannerView.classList.add('scanning-active');
    } else {
        startBtn.style.display = 'inline-block';
        stopBtn.style.display = 'none';
        placeholder.style.display = 'flex';
        scannerView.style.display = 'none';
        scannerView.classList.remove('scanning-active');
    }
}

// Process scanned QR code
function processQRCode(qrData) {
    console.log('QR Code detected:', qrData);
    
    // Stop scanner
    stopQRScanner();
    
    // Show processing
    showProcessing();
    
    // Send to server
    markAttendanceViaQR(qrData);
}

// Show processing animation
function showProcessing() {
    const scannerView = document.getElementById('scannerView');
    scannerView.innerHTML = `
        <div class="processing-overlay">
            <div class="processing-content text-center">
                <div class="spinner-border text-primary mb-3" style="width: 3rem; height: 3rem;" role="status">
                    <span class="visually-hidden">Processing...</span>
                </div>
                <h4>Processing QR Code</h4>
                <p class="text-muted">Verifying your attendance...</p>
            </div>
        </div>
    `;
}

// Show scanner error
function showScannerError(error) {
    const scannerView = document.getElementById('scannerView');
    scannerView.innerHTML = `
        <div class="error-overlay">
            <div class="error-content text-center">
                <i class="fas fa-exclamation-triangle fa-3x text-warning mb-3"></i>
                <h4>Scanner Error</h4>
                <p class="text-muted">${error}</p>
                <button class="btn btn-primary mt-3" onclick="startQRScanner()">
                    <i class="fas fa-redo me-2"></i>Try Again
                </button>
            </div>
        </div>
    `;
}

// Mark attendance via QR code
async function markAttendanceViaQR(qrData) {
    try {
        const response = await fetch('/attendance/mark/qr/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken(),
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: JSON.stringify({ qr_data: qrData })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showAttendanceSuccess(data);
            updateAttendanceStats();
        } else {
            showAttendanceError(data.message);
        }
    } catch (error) {
        console.error('Error:', error);
        showAttendanceError('Network error. Please try again.');
    }
}

// Helper function to get CSRF token
function getCSRFToken() {
    const cookieValue = document.cookie
        .split('; ')
        .find(row => row.startsWith('csrftoken='))
        ?.split('=')[1];
    return cookieValue || '';
}