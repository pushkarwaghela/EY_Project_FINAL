// ==============================================
// ULTIMATE FIX: Define ALL functions immediately
// ==============================================

// 1. Force light theme
localStorage.setItem('theme', 'light');

// 2. Define showToast IMMEDIATELY
window.showToast = function(message, type = 'info') {
    console.log(`[Toast ${type}] ${message}`);
};

// 3. Define startQRScanner IMMEDIATELY (CRITICAL!)
window.startQRScanner = function() {
    console.log('startQRScanner called (placeholder)');
    // This will be replaced by the real function later
};

console.log('✅ All critical functions defined');

// Continue with the rest of your code...

// Add at the VERY beginning of your script.js
localStorage.setItem('theme', 'light'); // Force light theme
window.showToast = function(message, type = 'info', duration = 3000) {
    console.log(`[Toast ${type.toUpperCase()}] ${message}`);
    // Implementation will be replaced by initializeUI()
};

// Prevent duplicate initialization
if (window.SCES_INITIALIZED) {
    console.log('SCES already initialized');
} else {
    window.SCES_INITIALIZED = true;

    document.addEventListener('DOMContentLoaded', function() {
        console.log('%c🎓 Smart College Event System v2.0 🚀', 'color: #4361ee; font-size: 16px; font-weight: bold;');
        console.log('%cBuilt with ❤️ for the competition', 'color: #7209b7; font-size: 12px;');
        
        // Initialize all modules
        initializeModules();
        
        // Setup theme
        setupTheme();
        
        // Setup performance monitoring
        setupPerformanceMonitoring();
    });
}

function initializeModules() {
    // Order matters - initialize core first
    initializeUI();
    initializeCore();
    initializeNavigation();
    initializeDashboard();
    initializeForms();
    initializeNotifications();
    initializeResponsive();
    initializeAnimations();
    initializeQRScanner();
    initializeAnalytics();
}

// ===== CORE MODULE =====
function initializeCore() {
    // Global error handler
    window.addEventListener('error', function(e) {
        console.error('Global error:', e.error);
        showToast('An unexpected error occurred', 'error');
    });
    
    // Unhandled promise rejection
    window.addEventListener('unhandledrejection', function(e) {
        console.error('Unhandled promise rejection:', e.reason);
        showToast('Operation failed. Please try again.', 'error');
    });
    
    // Initialize performance tracking
    if ('performance' in window) {
        console.log('Performance API available');
    }
}

// ===== NAVIGATION MODULE =====
function initializeNavigation() {
    // Enhanced active state with animation
    const currentPath = window.location.pathname;
    document.querySelectorAll('.navbar-nav .nav-link').forEach(link => {
        const href = link.getAttribute('href');
        if (href === currentPath || currentPath.includes(href.replace(/\/$/, ''))) {
            link.classList.add('active', 'animate__animated', 'animate__pulse');
            link.style.fontWeight = '700';
            
            // Add indicator
            const indicator = document.createElement('span');
            indicator.className = 'active-indicator';
            link.appendChild(indicator);
        }
    });
    
    // Smooth scrolling with offset
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const targetId = this.getAttribute('href');
            if (targetId === '#' || targetId === '') return;
            
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                e.preventDefault();
                const offset = 100;
                const targetPosition = targetElement.offsetTop - offset;
                
                window.scrollTo({
                    top: targetPosition,
                    behavior: 'smooth'
                });
                
                // Add focus for accessibility
                setTimeout(() => targetElement.setAttribute('tabindex', '-1'), 500);
            }
        });
    });
    
    // Mobile navigation enhancements
    const navbarToggler = document.querySelector('.navbar-toggler');
    if (navbarToggler) {
        navbarToggler.addEventListener('click', function() {
            const isExpanded = this.getAttribute('aria-expanded') === 'true';
            document.body.classList.toggle('mobile-nav-open', !isExpanded);
            
            // Animate hamburger to X
            this.classList.toggle('collapsed');
            const icon = this.querySelector('.navbar-toggler-icon');
            icon.classList.toggle('open');
        });
    }
    
    // Dropdown hover delay
    const dropdowns = document.querySelectorAll('.dropdown');
    dropdowns.forEach(dropdown => {
        let timeout;
        
        dropdown.addEventListener('mouseenter', () => {
            clearTimeout(timeout);
            const toggle = dropdown.querySelector('.dropdown-toggle');
            if (toggle) {
                const bsDropdown = bootstrap.Dropdown.getInstance(toggle) || new bootstrap.Dropdown(toggle);
                bsDropdown.show();
            }
        });
        
        dropdown.addEventListener('mouseleave', () => {
            timeout = setTimeout(() => {
                const toggle = dropdown.querySelector('.dropdown-toggle');
                if (toggle) {
                    const bsDropdown = bootstrap.Dropdown.getInstance(toggle);
                    if (bsDropdown) bsDropdown.hide();
                }
            }, 300);
        });
    });
}

// ===== DASHBOARD MODULE =====
function initializeDashboard() {
    // Animate elements on scroll
    const animateOnScroll = () => {
        const elements = document.querySelectorAll('.stat-card, .dashboard-card, .feature-icon');
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate__animated', 'animate__fadeInUp');
                    observer.unobserve(entry.target);
                }
            });
        }, { 
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        });
        
        elements.forEach(el => observer.observe(el));
    };
    
    // Initialize if elements exist
    if (document.querySelector('.stat-card')) {
        animateOnScroll();
        
        // Real-time clock
        function updateRealTimeClock() {
            const clockElements = document.querySelectorAll('#current-time, .current-time');
            if (clockElements.length > 0) {
                const now = new Date();
                const formatter = new Intl.DateTimeFormat('en-US', {
                    weekday: 'long',
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit',
                    second: '2-digit',
                    hour12: true
                });
                
                const timeString = formatter.format(now);
                clockElements.forEach(el => {
                    el.textContent = timeString;
                    el.setAttribute('title', `Last updated: ${now.toISOString()}`);
                });
            }
        }
        
        updateRealTimeClock();
        setInterval(updateRealTimeClock, 1000);
        
        // Live counter animation
        function animateCounters() {
            const counters = document.querySelectorAll('.counter-number');
            counters.forEach(counter => {
                const target = parseInt(counter.textContent.replace(/,/g, ''));
                if (!isNaN(target)) {
                    animateCounter(counter, target);
                }
            });
        }
        
        setTimeout(animateCounters, 1000);
    }
    
    // Card hover effects with 3D transform
    const cards = document.querySelectorAll('.dashboard-card, .hover-lift, .stat-card');
    cards.forEach(card => {
        card.addEventListener('mouseenter', function(e) {
            const rect = this.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            
            this.style.transform = `
                translateY(-10px) 
                scale(1.02) 
                rotateX(${(y / rect.height - 0.5) * 2}deg) 
                rotateY(${(x / rect.width - 0.5) * -2}deg)
            `;
            this.style.transition = 'transform 0.3s ease, box-shadow 0.3s ease';
            this.style.boxShadow = '0 20px 40px rgba(0,0,0,0.1)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1) rotateX(0) rotateY(0)';
            this.style.boxShadow = '';
        });
        
        card.addEventListener('mousemove', function(e) {
            const rect = this.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            
            this.style.setProperty('--mouse-x', `${x}px`);
            this.style.setProperty('--mouse-y', `${y}px`);
        });
    });
}

// ===== FORMS MODULE =====
function initializeForms() {
    // Enhanced floating labels
    document.querySelectorAll('.form-floating, .form-group').forEach(container => {
        const input = container.querySelector('.form-control, .form-select');
        if (!input) return;
        
        // Check initial state
        if (input.value) {
            container.classList.add('filled');
        }
        
        // Focus events
        input.addEventListener('focus', function() {
            container.classList.add('focused');
            this.parentElement.classList.add('focused');
        });
        
        input.addEventListener('blur', function() {
            container.classList.remove('focused');
            this.parentElement.classList.remove('focused');
            if (this.value) {
                container.classList.add('filled');
            } else {
                container.classList.remove('filled');
            }
        });
        
        // Input validation
        input.addEventListener('input', function() {
            validateField(this);
        });
    });
    
    // Form submission enhancement
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', async function(e) {
            // Validate all fields
            const isValid = validateForm(this);
            
            if (!isValid) {
                e.preventDefault();
                showToast('Please correct the errors in the form', 'warning');
                return;
            }
            
            // Show loading state
            const submitButton = this.querySelector('button[type="submit"]');
            if (submitButton) {
                const originalText = submitButton.innerHTML;
                submitButton.innerHTML = `
                    <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
                    Processing...
                `;
                submitButton.disabled = true;
                
                // Reset button after delay or on error
                setTimeout(() => {
                    submitButton.innerHTML = originalText;
                    submitButton.disabled = false;
                }, 5000);
            }
        });
    });
    
    // Password strength meter
    const passwordInputs = document.querySelectorAll('input[type="password"]');
    passwordInputs.forEach(input => {
        if (input.id.includes('password')) {
            setupPasswordStrength(input);
        }
    });
    
    // Character counter for textareas
    document.querySelectorAll('textarea[maxlength]').forEach(textarea => {
        const maxLength = parseInt(textarea.getAttribute('maxlength'));
        const counter = document.createElement('small');
        counter.className = 'char-counter text-muted';
        counter.style.float = 'right';
        counter.style.fontSize = '0.8rem';
        counter.textContent = `0/${maxLength}`;
        
        textarea.parentNode.appendChild(counter);
        
        textarea.addEventListener('input', function() {
            const length = this.value.length;
            counter.textContent = `${length}/${maxLength}`;
            
            if (length > maxLength * 0.9) {
                counter.classList.add('text-warning');
            } else {
                counter.classList.remove('text-warning');
            }
            
            if (length >= maxLength) {
                counter.classList.add('text-danger');
            } else {
                counter.classList.remove('text-danger');
            }
        });
    });
}

// ===== UI MODULE =====
function initializeUI() {
    // Toast notification system
    window.showToast = function(message, type = 'info', duration = 3000) {
        const toastId = 'toast-' + Date.now();
        const icons = {
            success: 'fa-check-circle',
            error: 'fa-exclamation-circle',
            warning: 'fa-exclamation-triangle',
            info: 'fa-info-circle'
        };
        
        const toastHtml = `
            <div id="${toastId}" class="toast-notification toast-${type}" role="alert">
                <div class="toast-icon">
                    <i class="fas ${icons[type] || 'fa-info-circle'}"></i>
                </div>
                <div class="toast-content">
                    <div class="toast-message">${message}</div>
                    <small class="toast-time">${new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</small>
                </div>
                <button class="toast-close" aria-label="Close">
                    <i class="fas fa-times"></i>
                </button>
                <div class="toast-progress"></div>
            </div>
        `;
        
        const toastContainer = document.querySelector('.toast-container');
        if (!toastContainer) {
            const container = document.createElement('div');
            container.className = 'toast-container';
            document.body.appendChild(container);
        }
        
        document.querySelector('.toast-container').insertAdjacentHTML('afterbegin', toastHtml);
        const toastEl = document.getElementById(toastId);
        
        // Animate in
        setTimeout(() => toastEl.classList.add('show'), 10);
        
        // Progress bar animation
        const progressBar = toastEl.querySelector('.toast-progress');
        progressBar.style.animation = `toastProgress ${duration}ms linear`;
        
        // Auto dismiss
        const dismissTimeout = setTimeout(() => {
            dismissToast(toastId);
        }, duration);
        
        // Close button
        toastEl.querySelector('.toast-close').addEventListener('click', () => {
            clearTimeout(dismissTimeout);
            dismissToast(toastId);
        });
        
        // Hover pause
        toastEl.addEventListener('mouseenter', () => {
            progressBar.style.animationPlayState = 'paused';
        });
        
        toastEl.addEventListener('mouseleave', () => {
            progressBar.style.animationPlayState = 'running';
        });
        
        function dismissToast(id) {
            const toast = document.getElementById(id);
            if (toast) {
                toast.classList.remove('show');
                setTimeout(() => toast.remove(), 300);
            }
        }
    };
    
    // Tooltip initialization with delay
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    if (tooltipTriggerList.length > 0) {
        tooltipTriggerList.forEach(trigger => {
            new bootstrap.Tooltip(trigger, {
                delay: { show: 300, hide: 100 },
                trigger: 'hover focus'
            });
        });
    }
    
    // Popover initialization
    const popoverTriggerList = document.querySelectorAll('[data-bs-toggle="popover"]');
    if (popoverTriggerList.length > 0) {
        popoverTriggerList.forEach(trigger => {
            new bootstrap.Popover(trigger, {
                trigger: 'focus',
                html: true
            });
        });
    }
    
    // Modal enhancements
    document.querySelectorAll('.modal').forEach(modal => {
        modal.addEventListener('show.bs.modal', function() {
            document.body.classList.add('modal-open');
        });
        
        modal.addEventListener('hidden.bs.modal', function() {
            document.body.classList.remove('modal-open');
        });
    });
    
    // Auto-dismiss alerts
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(alert => {
        const closeButton = alert.querySelector('.btn-close');
        if (!closeButton) {
            const closeBtn = document.createElement('button');
            closeBtn.className = 'btn-close';
            closeBtn.setAttribute('data-bs-dismiss', 'alert');
            closeBtn.setAttribute('aria-label', 'Close');
            alert.appendChild(closeBtn);
        }
        
        setTimeout(() => {
            if (alert.parentNode) {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }
        }, 5000);
    });
}

// ===== NOTIFICATIONS MODULE =====
function initializeNotifications() {
    // Live notification updates
    const notificationUrl = document.querySelector('[data-notifications-url]');
    if (notificationUrl) {
        const url = notificationUrl.dataset.notificationsUrl;
        
        // Initial check
        checkNotifications(url);
        
        // Periodic checks
        setInterval(() => checkNotifications(url), 30000);
        
        // WebSocket connection for real-time (if available)
        if ('WebSocket' in window) {
            setupWebSocketNotifications();
        }
    }
    
    // Mark as read with animation
    document.querySelectorAll('.mark-as-read').forEach(button => {
        button.addEventListener('click', function() {
            const notificationId = this.dataset.notificationId;
            const notificationItem = this.closest('.notification-item');
            
            // Animate out
            notificationItem.style.transition = 'all 0.3s ease';
            notificationItem.style.opacity = '0';
            notificationItem.style.transform = 'translateX(100%)';
            
            setTimeout(() => {
                markNotificationAsRead(notificationId, notificationItem);
            }, 300);
        });
    });
    
    // Notification sound (optional)
    function playNotificationSound() {
        try {
            const audio = new Audio('/static/sounds/notification.mp3');
            audio.volume = 0.3;
            audio.play();
        } catch (e) {
            console.log('Notification sound not available');
        }
    }
}

// ===== RESPONSIVE MODULE =====
function initializeResponsive() {
    // Handle responsive breakpoints
    const breakpoints = {
        sm: 576,
        md: 768,
        lg: 992,
        xl: 1200,
        xxl: 1400
    };
    
    let currentBreakpoint = getCurrentBreakpoint();
    
    window.addEventListener('resize', debounce(() => {
        const newBreakpoint = getCurrentBreakpoint();
        if (newBreakpoint !== currentBreakpoint) {
            currentBreakpoint = newBreakpoint;
            handleBreakpointChange(newBreakpoint);
        }
        
        // Update responsive classes
        updateResponsiveClasses();
    }, 250));
    
    // Touch device detection
    if ('ontouchstart' in window || navigator.maxTouchPoints > 0) {
        document.documentElement.classList.add('touch-device');
        
        // Add touch feedback
        document.querySelectorAll('.btn, .card, .nav-link, .list-group-item').forEach(element => {
            element.addEventListener('touchstart', function() {
                this.classList.add('touch-active');
            });
            
            element.addEventListener('touchend', function() {
                setTimeout(() => this.classList.remove('touch-active'), 150);
            });
        });
    }
    
    // Mobile view optimizations
    if (window.innerWidth < breakpoints.md) {
        optimizeForMobile();
    }
}

// ===== ANIMATIONS MODULE =====
function initializeAnimations() {
    // Parallax effect for hero sections
    const heroSection = document.querySelector('.hero-section');
    if (heroSection) {
        window.addEventListener('scroll', () => {
            const scrolled = window.pageYOffset;
            const rate = scrolled * -0.5;
            heroSection.style.transform = `translate3d(0, ${rate}px, 0)`;
        });
    }
    
    // Stagger animations for lists
    document.querySelectorAll('.list-group, .row').forEach(container => {
        const items = container.children;
        Array.from(items).forEach((item, index) => {
            item.style.animationDelay = `${index * 0.1}s`;
            item.classList.add('animate__animated', 'animate__fadeIn');
        });
    });
    
    // Page transition effect
    document.querySelectorAll('a:not([href^="#"])').forEach(link => {
        link.addEventListener('click', function(e) {
            if (!this.target && !this.href.includes('#')) {
                e.preventDefault();
                const href = this.href;
                
                // Add page transition
                document.body.classList.add('page-transition');
                
                setTimeout(() => {
                    window.location.href = href;
                }, 300);
            }
        });
    });
}

// ===== QR SCANNER MODULE =====
function initializeQRScanner() {
    if (typeof Html5Qrcode !== 'undefined') {
        window.startQRScanner = function(containerId = 'scanner-container', resultId = 'qr-result') {
            const container = document.getElementById(containerId);
            const resultDiv = document.getElementById(resultId);
            
            if (!container || !resultDiv) {
                console.error('QR scanner containers not found');
                return;
            }
            
            // Clear previous scanner
            container.innerHTML = '';
            resultDiv.innerHTML = '';
            
            // Show loading state
            resultDiv.innerHTML = `
                <div class="text-center">
                    <div class="spinner-border text-primary mb-3" role="status">
                        <span class="visually-hidden">Initializing scanner...</span>
                    </div>
                    <p>Initializing camera...</p>
                </div>
            `;
            
            // Initialize scanner with better config
            const html5QrCode = new Html5Qrcode(containerId);
            const config = { 
                fps: 30,
                qrbox: { width: 250, height: 250 },
                aspectRatio: 1.0,
                disableFlip: false,
                videoConstraints: {
                    facingMode: { exact: "environment" }
                }
            };
            
            html5QrCode.start(
                { facingMode: "environment" },
                config,
                onScanSuccess,
                onScanError
            ).catch(onScannerStartError);
            
            function onScanSuccess(decodedText) {
                html5QrCode.stop();
                resultDiv.innerHTML = `
                    <div class="alert alert-success animate__animated animate__bounceIn">
                        <i class="fas fa-check-circle me-2"></i>
                        <strong>QR Code Scanned Successfully!</strong>
                        <div class="mt-2">
                            <code class="bg-light p-2 rounded d-block">${decodedText.substring(0, 50)}...</code>
                        </div>
                    </div>
                    <div class="text-center mt-3">
                        <div class="spinner-border text-primary" role="status">
                            <span class="visually-hidden">Processing...</span>
                        </div>
                        <p class="mt-2">Processing attendance...</p>
                    </div>
                `;
                
                processQRCode(decodedText);
            }
            
            function onScanError(errorMessage) {
                // Ignore common scan errors
                if (!errorMessage.includes('NotFoundException')) {
                    console.log('QR scan error:', errorMessage);
                }
            }
            
            function onScannerStartError(error) {
                resultDiv.innerHTML = `
                    <div class="alert alert-danger">
                        <i class="fas fa-exclamation-circle me-2"></i>
                        <strong>Camera Error</strong>
                        <p class="mt-2">${error.message}</p>
                        <button class="btn btn-sm btn-outline-primary mt-2" onclick="startQRScanner()">
                            Try Again
                        </button>
                    </div>
                `;
            }
            
            function processQRCode(qrData) {
                fetch('/attendance/mark-qr/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken'),
                    },
                    body: JSON.stringify({ qr_data: qrData })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        resultDiv.innerHTML = `
                            <div class="alert alert-success">
                                <i class="fas fa-check-circle me-2 fa-2x"></i>
                                <div>
                                    <h5>Success!</h5>
                                    <p>${data.message}</p>
                                    ${data.event ? `<p><strong>Event:</strong> ${data.event.title}</p>` : ''}
                                    <p class="text-muted small">${new Date().toLocaleTimeString()}</p>
                                </div>
                            </div>
                            <div class="text-center mt-3">
                                <button class="btn btn-primary" onclick="startQRScanner()">
                                    <i class="fas fa-redo me-1"></i> Scan Another
                                </button>
                            </div>
                        `;
                        
                        // Show success animation
                        const successIcon = resultDiv.querySelector('.fa-check-circle');
                        successIcon.classList.add('animate__animated', 'animate__tada');
                        
                        // Play success sound
                        playSuccessSound();
                        
                        // Update attendance stats
                        updateAttendanceStats();
                    } else {
                        resultDiv.innerHTML = `
                            <div class="alert alert-danger">
                                <i class="fas fa-exclamation-circle me-2"></i>
                                <div>
                                    <h5>Error</h5>
                                    <p>${data.message}</p>
                                </div>
                            </div>
                            <div class="text-center mt-3">
                                <button class="btn btn-primary" onclick="startQRScanner()">
                                    <i class="fas fa-redo me-1"></i> Try Again
                                </button>
                            </div>
                        `;
                    }
                })
                .catch(error => {
                    resultDiv.innerHTML = `
                        <div class="alert alert-danger">
                            <i class="fas fa-exclamation-circle me-2"></i>
                            <div>
                                <h5>Network Error</h5>
                                <p>Please check your connection and try again.</p>
                                <p class="text-muted small">${error.message}</p>
                            </div>
                        </div>
                        <div class="text-center mt-3">
                            <button class="btn btn-primary" onclick="startQRScanner()">
                                <i class="fas fa-redo me-1"></i> Try Again
                            </button>
                        </div>
                    `;
                });
            }
        };
    }
}

// ===== ANALYTICS MODULE =====
function initializeAnalytics() {
    // Track page views
    trackPageView();
    
    // Track user interactions
    document.querySelectorAll('[data-track]').forEach(element => {
        element.addEventListener('click', function() {
            const eventName = this.dataset.track;
            trackEvent(eventName, {
                element: this.tagName,
                text: this.textContent.trim(),
                href: this.href
            });
        });
    });
    
    // Performance monitoring
    if ('PerformanceObserver' in window) {
        const observer = new PerformanceObserver((list) => {
            for (const entry of list.getEntries()) {
                if (entry.entryType === 'longtask') {
                    console.warn('Long task detected:', entry);
                }
            }
        });
        
        observer.observe({ entryTypes: ['longtask'] });
    }
}

// ===== UTILITY FUNCTIONS =====
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

function debounce(func, wait, immediate) {
    let timeout;
    return function executedFunction() {
        const context = this;
        const args = arguments;
        const later = function() {
            timeout = null;
            if (!immediate) func.apply(context, args);
        };
        const callNow = immediate && !timeout;
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
        if (callNow) func.apply(context, args);
    };
}

function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

function animateCounter(element, target, duration = 1000) {
    const start = 0;
    const increment = target / (duration / 16);
    let current = start;
    
    const timer = setInterval(() => {
        current += increment;
        if (current >= target) {
            element.textContent = target.toLocaleString();
            clearInterval(timer);
        } else {
            element.textContent = Math.floor(current).toLocaleString();
        }
    }, 16);
}

function validateField(field) {
    const isValid = field.checkValidity();
    const container = field.closest('.form-floating, .form-group');
    
    if (isValid) {
        field.classList.remove('is-invalid');
        field.classList.add('is-valid');
        if (container) container.classList.remove('has-error');
    } else {
        field.classList.remove('is-valid');
        field.classList.add('is-invalid');
        if (container) container.classList.add('has-error');
        
        // Show error message
        const errorId = field.id + '-error';
        let errorElement = document.getElementById(errorId);
        if (!errorElement) {
            errorElement = document.createElement('div');
            errorElement.id = errorId;
            errorElement.className = 'invalid-feedback';
            field.parentNode.appendChild(errorElement);
        }
        errorElement.textContent = field.validationMessage;
    }
    
    return isValid;
}

function validateForm(form) {
    let isValid = true;
    const fields = form.querySelectorAll('input, select, textarea');
    
    fields.forEach(field => {
        if (!validateField(field)) {
            isValid = false;
        }
    });
    
    return isValid;
}

function setupPasswordStrength(input) {
    const container = input.parentNode;
    const strengthMeter = document.createElement('div');
    strengthMeter.className = 'password-strength mt-2';
    strengthMeter.innerHTML = `
        <div class="strength-meter">
            <div class="strength-bar"></div>
        </div>
        <small class="strength-text"></small>
        <ul class="strength-requirements list-unstyled mt-1 small">
            <li data-requirement="length"><i class="fas fa-times text-danger"></i> At least 8 characters</li>
            <li data-requirement="uppercase"><i class="fas fa-times text-danger"></i> One uppercase letter</li>
            <li data-requirement="number"><i class="fas fa-times text-danger"></i> One number</li>
            <li data-requirement="special"><i class="fas fa-times text-danger"></i> One special character</li>
        </ul>
    `;
    
    container.appendChild(strengthMeter);
    
    input.addEventListener('input', function() {
        const password = this.value;
        const strength = calculatePasswordStrength(password);
        
        // Update strength bar
        const bar = strengthMeter.querySelector('.strength-bar');
        const text = strengthMeter.querySelector('.strength-text');
        bar.style.width = `${strength.score * 25}%`;
        bar.className = `strength-bar ${strength.class}`;
        text.textContent = strength.text;
        text.className = `strength-text text-${strength.class}`;
        
        // Update requirements
        updatePasswordRequirements(password, strengthMeter);
    });
}

function calculatePasswordStrength(password) {
    let score = 0;
    const requirements = {
        length: password.length >= 8,
        uppercase: /[A-Z]/.test(password),
        number: /[0-9]/.test(password),
        special: /[^A-Za-z0-9]/.test(password)
    };
    
    Object.values(requirements).forEach(req => {
        if (req) score++;
    });
    
    const strengthMap = [
        { class: 'danger', text: 'Very Weak' },
        { class: 'warning', text: 'Weak' },
        { class: 'info', text: 'Fair' },
        { class: 'success', text: 'Strong' },
        { class: 'success', text: 'Very Strong' }
    ];
    
    return {
        score: score,
        class: strengthMap[score].class,
        text: strengthMap[score].text,
        requirements: requirements
    };
}

function updatePasswordRequirements(password, container) {
    const requirements = {
        length: password.length >= 8,
        uppercase: /[A-Z]/.test(password),
        number: /[0-9]/.test(password),
        special: /[^A-Za-z0-9]/.test(password)
    };
    
    Object.entries(requirements).forEach(([key, met]) => {
        const requirementEl = container.querySelector(`[data-requirement="${key}"]`);
        if (requirementEl) {
            const icon = requirementEl.querySelector('i');
            icon.className = met ? 'fas fa-check text-success' : 'fas fa-times text-danger';
            requirementEl.style.opacity = met ? '0.7' : '1';
        }
    });
}

function setupTheme() {
    // Check for saved theme or prefer-color-scheme
    const savedTheme = localStorage.getItem('theme');
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    
    if (savedTheme === 'dark' || (!savedTheme && prefersDark)) {
        enableDarkTheme();
    }
    
    // Theme toggle
    const themeToggle = document.getElementById('themeToggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', () => {
            if (document.body.classList.contains('dark-theme')) {
                disableDarkTheme();
            } else {
                enableDarkTheme();
            }
        });
    }
    
    // Listen for system theme changes
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
        if (!localStorage.getItem('theme')) {
            if (e.matches) {
                enableDarkTheme();
            } else {
                disableDarkTheme();
            }
        }
    });
}

function enableDarkTheme() {
    document.body.classList.add('dark-theme');
    localStorage.setItem('theme', 'dark');
    updateThemeIcon('sun');
}

function disableDarkTheme() {
    document.body.classList.remove('dark-theme');
    localStorage.setItem('theme', 'light');
    updateThemeIcon('moon');
}

function updateThemeIcon(icon) {
    const themeToggle = document.getElementById('themeToggle');
    if (themeToggle) {
        themeToggle.innerHTML = `<i class="fas fa-${icon}"></i>`;
    }
}

function setupPerformanceMonitoring() {
    // Log performance metrics
    if ('performance' in window) {
        window.addEventListener('load', () => {
            setTimeout(() => {
                const perfData = performance.getEntriesByType('navigation')[0];
                if (perfData) {
                    console.table({
                        'DOM Load': `${perfData.domContentLoadedEventEnd - perfData.domContentLoadedEventStart}ms`,
                        'Page Load': `${perfData.loadEventEnd - perfData.loadEventStart}ms`,
                        'Total Time': `${perfData.loadEventEnd - perfData.startTime}ms`
                    });
                }
            }, 0);
        });
    }
}

function getCurrentBreakpoint() {
    const width = window.innerWidth;
    if (width >= 1400) return 'xxl';
    if (width >= 1200) return 'xl';
    if (width >= 992) return 'lg';
    if (width >= 768) return 'md';
    if (width >= 576) return 'sm';
    return 'xs';
}

function handleBreakpointChange(breakpoint) {
    console.log(`Breakpoint changed to: ${breakpoint}`);
    
    // Update responsive attributes
    document.documentElement.setAttribute('data-breakpoint', breakpoint);
    
    // Trigger breakpoint-specific actions
    switch (breakpoint) {
        case 'xs':
        case 'sm':
            optimizeForMobile();
            break;
        case 'md':
            optimizeForTablet();
            break;
        default:
            optimizeForDesktop();
    }
}

function optimizeForMobile() {
    // Mobile optimizations
    document.body.classList.add('mobile-optimized');
    
    // Lazy load more aggressively
    if ('IntersectionObserver' in window) {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    if (img.dataset.src) {
                        img.src = img.dataset.src;
                        img.classList.remove('lazy');
                        observer.unobserve(img);
                    }
                }
            });
        }, { threshold: 0.1 });
        
        document.querySelectorAll('img.lazy').forEach(img => observer.observe(img));
    }
}

function optimizeForTablet() {
    // Tablet optimizations
    document.body.classList.add('tablet-optimized');
}

function optimizeForDesktop() {
    // Desktop optimizations
    document.body.classList.add('desktop-optimized');
}

function updateResponsiveClasses() {
    const width = window.innerWidth;
    const height = window.innerHeight;
    
    // Orientation
    if (width > height) {
        document.body.classList.add('landscape');
        document.body.classList.remove('portrait');
    } else {
        document.body.classList.add('portrait');
        document.body.classList.remove('landscape');
    }
    
    // High DPI screens
    if (window.devicePixelRatio > 1) {
        document.body.classList.add('high-dpi');
    }
}

function checkNotifications(url) {
    fetch(url, {
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.unread_count > 0) {
            updateNotificationBadge(data.unread_count);
            
            // Show desktop notification
            if (data.latest_notification && Notification.permission === 'granted') {
                showDesktopNotification(data.latest_notification);
            }
        }
    })
    .catch(error => console.error('Error checking notifications:', error));
}

function setupWebSocketNotifications() {
    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${wsProtocol}//${window.location.host}/ws/notifications/`;
    
    try {
        const socket = new WebSocket(wsUrl);
        
        socket.onopen = function() {
            console.log('WebSocket connected for notifications');
        };
        
        socket.onmessage = function(event) {
            const data = JSON.parse(event.data);
            if (data.type === 'notification') {
                handleRealTimeNotification(data);
            }
        };
        
        socket.onclose = function() {
            console.log('WebSocket disconnected');
            // Attempt to reconnect after delay
            setTimeout(setupWebSocketNotifications, 5000);
        };
    } catch (error) {
        console.error('WebSocket error:', error);
    }
}

function handleRealTimeNotification(data) {
    // Update badge
    updateNotificationBadge(data.unread_count);
    
    // Show toast
    showToast(data.message, 'info');
    
    // Play sound
    playNotificationSound();
    
    // Update notification list if open
    const notificationList = document.querySelector('.notification-list');
    if (notificationList) {
        addNotificationToList(data.notification);
    }
}

function markNotificationAsRead(notificationId, element) {
    console.log(`Marking notification ${notificationId} as read...`);
    
    const csrftoken = getCookie('csrftoken');
    if (!csrftoken) {
        console.error('CSRF token not found');
        showToast('Session error. Please refresh the page.', 'error');
        return;
    }
    
    fetch(`/api/notifications/${notificationId}/mark-read/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,
            'X-Requested-With': 'XMLHttpRequest'
        },
        body: JSON.stringify({
            notification_id: notificationId,
            timestamp: new Date().toISOString()
        })
    })
    .then(response => {
        console.log('Response status:', response.status, response.statusText);
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        return response.json();  // Parse JSON
    })
    .then(data => {
        console.log('Mark read response:', data);
        
        if (data.success) {
            showToast('Notification marked as read', 'success');
            
            // Animate and remove the notification element
            if (element) {
                element.style.transition = 'all 0.3s ease';
                element.style.opacity = '0';
                element.style.transform = 'translateX(100%)';
                
                setTimeout(() => {
                    if (element && element.parentNode) {
                        element.remove();
                        
                        // If no notifications left, show message
                        const notificationList = document.querySelector('.notification-list');
                        if (notificationList && notificationList.children.length === 0) {
                            notificationList.innerHTML = `
                                <div class="text-center py-5 text-muted">
                                    <i class="fas fa-bell-slash fa-3x mb-3"></i>
                                    <p>No notifications</p>
                                </div>
                            `;
                        }
                    }
                }, 300);
            }
            
            // Update badge count
            if (data.unread_count !== undefined) {
                updateNotificationBadge(data.unread_count);
            }
            
        } else {
            showToast(data.error || 'Failed to mark as read', 'error');
        }
    })
    .catch(error => {
        console.error('Error marking notification as read:', error);
        showToast(`Error: ${error.message}`, 'error');
        
        // Restore element if error
        if (element) {
            element.style.opacity = '1';
            element.style.transform = 'translateX(0)';
        }
    });
}

function updateNotificationBadge(count) {
    const badges = document.querySelectorAll('.notification-badge, .badge[data-notification-count]');
    badges.forEach(badge => {
        if (count > 0) {
            badge.textContent = count > 99 ? '99+' : count;
            badge.style.display = 'inline-block';
            
            // Add pulse animation
            badge.classList.add('pulse');
            setTimeout(() => badge.classList.remove('pulse'), 1000);
        } else {
            badge.style.display = 'none';
        }
    });
    
    // Update document title
    if (count > 0) {
        document.title = `(${count}) ${document.title.replace(/^\(\d+\)\s*/, '')}`;
    } else {
        document.title = document.title.replace(/^\(\d+\)\s*/, '');
    }
}

function showDesktopNotification(notification) {
    if (!('Notification' in window)) return;
    
    if (Notification.permission === 'granted') {
        new Notification(notification.title, {
            body: notification.message,
            icon: '/static/favicon.ico',
            tag: 'sces-notification'
        });
    } else if (Notification.permission !== 'denied') {
        Notification.requestPermission().then(permission => {
            if (permission === 'granted') {
                new Notification(notification.title, {
                    body: notification.message,
                    icon: '/static/favicon.ico'
                });
            }
        });
    }
}

function addNotificationToList(notification) {
    const notificationList = document.querySelector('.notification-list');
    if (!notificationList) return;
    
    const notificationHtml = `
        <div class="notification-item new animate__animated animate__fadeIn">
            <div class="notification-content">
                <h6>${notification.title}</h6>
                <p class="small text-muted">${notification.message}</p>
                <small class="text-muted">Just now</small>
            </div>
            <button class="btn btn-sm btn-outline-secondary mark-as-read" 
                    data-notification-id="${notification.id}">
                <i class="fas fa-check"></i>
            </button>
        </div>
    `;
    
    notificationList.insertAdjacentHTML('afterbegin', notificationHtml);
    
    // Add click handler to new button
    const newButton = notificationList.querySelector('.mark-as-read');
    if (newButton) {
        newButton.addEventListener('click', function() {
            markNotificationAsRead(this.dataset.notificationId, this.closest('.notification-item'));
        });
    }
}

function playSuccessSound() {
    try {
        const audioContext = new (window.AudioContext || window.webkitAudioContext)();
        const oscillator = audioContext.createOscillator();
        const gainNode = audioContext.createGain();
        
        oscillator.connect(gainNode);
        gainNode.connect(audioContext.destination);
        
        oscillator.frequency.setValueAtTime(523.25, audioContext.currentTime); // C5
        oscillator.frequency.setValueAtTime(659.25, audioContext.currentTime + 0.1); // E5
        oscillator.frequency.setValueAtTime(783.99, audioContext.currentTime + 0.2); // G5
        
        gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.3);
        
        oscillator.start();
        oscillator.stop(audioContext.currentTime + 0.3);
    } catch (e) {
        console.log('Audio not supported');
    }
}

function playNotificationSound() {
    // Simple beep sound
    try {
        const audioContext = new (window.AudioContext || window.webkitAudioContext)();
        const oscillator = audioContext.createOscillator();
        const gainNode = audioContext.createGain();
        
        oscillator.connect(gainNode);
        gainNode.connect(audioContext.destination);
        
        oscillator.frequency.value = 800;
        oscillator.type = 'sine';
        
        gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.1);
        
        oscillator.start();
        oscillator.stop(audioContext.currentTime + 0.1);
    } catch (e) {
        // Fallback to HTML5 audio
        try {
            const audio = new Audio('data:audio/wav;base64,UklGRigAAABXQVZFZm10IBIAAAABAAEAQB8AAEAfAAABAAgAZGF0YQ');
            audio.volume = 0.1;
            audio.play();
        } catch (e2) {
            console.log('Sound not supported');
        }
    }
}

function trackPageView() {
    const data = {
        page: window.location.pathname,
        referrer: document.referrer,
        timestamp: new Date().toISOString(),
        userAgent: navigator.userAgent,
        screen: `${window.screen.width}x${window.screen.height}`
    };
    
    // Send to analytics endpoint
    fetch('/api/analytics/pageview/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify(data)
    }).catch(() => {
        // Silently fail if analytics endpoint is not available
    });
}

function trackEvent(eventName, properties = {}) {
    const data = {
        event: eventName,
        properties: properties,
        timestamp: new Date().toISOString(),
        url: window.location.href
    };
    
    // Send to analytics endpoint
    fetch('/api/analytics/event/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify(data)
    }).catch(() => {
        // Silently fail if analytics endpoint is not available
    });
}

function updateAttendanceStats() {
    // Refresh attendance stats on dashboard
    const attendanceStats = document.querySelector('[data-attendance-stats]');
    if (attendanceStats) {
        const url = attendanceStats.dataset.attendanceStats;
        fetch(url)
            .then(response => response.json())
            .then(data => {
                // Update DOM with new stats
                if (data.attended_events !== undefined) {
                    const element = document.querySelector('[data-stat="attended-events"]');
                    if (element) animateCounter(element, data.attended_events);
                }
                
                if (data.attendance_rate !== undefined) {
                    const element = document.querySelector('[data-stat="attendance-rate"]');
                    if (element) {
                        element.textContent = `${data.attendance_rate}%`;
                        element.classList.add('animate__animated', 'animate__pulse');
                        setTimeout(() => element.classList.remove('animate__pulse'), 1000);
                    }
                }
            })
            .catch(error => console.error('Error updating attendance stats:', error));
    }
}

// ===== EXPORT GLOBALLY =====
window.SCES = {
    // Core functions
    showToast,
    startQRScanner,
    getCookie,
    
    // Utility functions
    debounce,
    throttle,
    animateCounter,
    validateForm,
    
    // Theme functions
    enableDarkTheme,
    disableDarkTheme,
    
    // Notification functions
    updateNotificationBadge,
    
    // Analytics functions
    trackEvent,
    
    // Version
    version: '2.0.0'
};

// ===== ADDITIONAL STYLES =====
const enhancedStyles = `
/* Active navigation indicator */
.nav-link.active .active-indicator {
    position: absolute;
    bottom: 0;
    left: 50%;
    transform: translateX(-50%);
    width: 4px;
    height: 4px;
    background: var(--primary);
    border-radius: 50%;
    animation: pulse 2s infinite;
}

/* Toast notifications */
.toast-container {
    position: fixed;
    top: 20px;
    right: 20px;
    z-index: 99999;
    display: flex;
    flex-direction: column;
    gap: 10px;
    max-width: 350px;
}

.toast-notification {
    background: white;
    border-radius: 10px;
    box-shadow: 0 5px 20px rgba(0,0,0,0.15);
    display: flex;
    align-items: center;
    padding: 15px;
    position: relative;
    overflow: hidden;
    transform: translateX(100%);
    opacity: 0;
    transition: all 0.3s ease;
}

.toast-notification.show {
    transform: translateX(0);
    opacity: 1;
}

.toast-icon {
    font-size: 1.5rem;
    margin-right: 15px;
    width: 40px;
    height: 40px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
}

.toast-success .toast-icon {
    background: rgba(46, 196, 182, 0.1);
    color: #2ec4b6;
}

.toast-error .toast-icon {
    background: rgba(231, 29, 54, 0.1);
    color: #e71d36;
}

.toast-warning .toast-icon {
    background: rgba(255, 159, 28, 0.1);
    color: #ff9f1c;
}

.toast-info .toast-icon {
    background: rgba(67, 97, 238, 0.1);
    color: #4361ee;
}

.toast-content {
    flex: 1;
}

.toast-message {
    font-weight: 500;
    margin-bottom: 3px;
}

.toast-time {
    font-size: 0.8rem;
    opacity: 0.7;
}

.toast-close {
    background: none;
    border: none;
    color: #999;
    cursor: pointer;
    padding: 5px;
    margin-left: 10px;
    font-size: 1.2rem;
    transition: color 0.3s ease;
}

.toast-close:hover {
    color: #666;
}

.toast-progress {
    position: absolute;
    bottom: 0;
    left: 0;
    height: 3px;
    background: currentColor;
    opacity: 0.3;
    width: 100%;
    transform-origin: left;
}

@keyframes toastProgress {
    from { transform: scaleX(1); }
    to { transform: scaleX(0); }
}

/* Password strength */
.strength-meter {
    height: 5px;
    background: #e9ecef;
    border-radius: 3px;
    overflow: hidden;
    margin-bottom: 5px;
}

.strength-bar {
    height: 100%;
    transition: width 0.3s ease, background-color 0.3s ease;
}

.strength-bar.danger { background: #e71d36; }
.strength-bar.warning { background: #ff9f1c; }
.strength-bar.info { background: #4361ee; }
.strength-bar.success { background: #2ec4b6; }

.strength-text {
    font-size: 0.85rem;
}

.strength-requirements {
    font-size: 0.8rem;
    color: #666;
    margin-top: 5px;
}

.strength-requirements li {
    margin-bottom: 2px;
    transition: opacity 0.3s ease;
}

/* Notification badges */
.notification-badge {
    animation: pulse 2s infinite;
}

@keyframes pulse {
    0% { transform: scale(1); }
    50% { transform: scale(1.1); }
    100% { transform: scale(1); }
}

/* Page transitions */
.page-transition {
    animation: fadeOut 0.3s ease forwards;
}

@keyframes fadeOut {
    from { opacity: 1; }
    to { opacity: 0; }
}

/* Dark theme */
.dark-theme {
    --bg-color: #1a1a1a;
    --text-color: #ffffff;
    --card-bg: #2d2d2d;
    --border-color: #404040;
    background: var(--bg-color);
    color: var(--text-color);
}

.dark-theme .dashboard-card {
    background: var(--card-bg);
    border-color: var(--border-color);
}

.dark-theme .stat-card {
    background: linear-gradient(135deg, #3a56d4 0%, #6209a7 100%);
}

/* Responsive helpers */
.mobile-optimized .dashboard-card {
    padding: 15px;
    margin-bottom: 15px;
}

.tablet-optimized .row {
    margin-left: -10px;
    margin-right: -10px;
}

.desktop-optimized .container {
    max-width: 1400px;
}

/* Touch feedback */
.touch-active {
    opacity: 0.8;
    transform: scale(0.98);
}

/* Character counter */
.char-counter {
    font-size: 0.8rem;
    color: #666;
    transition: color 0.3s ease;
}

.char-counter.text-warning {
    color: #ff9f1c;
}

.char-counter.text-danger {
    color: #e71d36;
}

/* Active form states */
.form-group.focused .form-control {
    border-color: #4361ee;
    box-shadow: 0 0 0 0.25rem rgba(67, 97, 238, 0.25);
}

.form-group.has-error .form-control {
    border-color: #e71d36;
}

/* Custom scrollbar for dark theme */
.dark-theme::-webkit-scrollbar {
    width: 10px;
}

.dark-theme::-webkit-scrollbar-track {
    background: #2d2d2d;
}

.dark-theme::-webkit-scrollbar-thumb {
    background: #555;
    border-radius: 5px;
}

.dark-theme::-webkit-scrollbar-thumb:hover {
    background: #666;
}

/* Print styles */
@media print {
    .no-print,
    .navbar,
    .footer,
    .btn,
    .toast-container,
    .theme-toggle {
        display: none !important;
    }
    
    .dashboard-card {
        break-inside: avoid;
        box-shadow: none !important;
        border: 1px solid #ddd !important;
    }
}
`;

// Inject styles
const styleElement = document.createElement('style');
styleElement.textContent = enhancedStyles;
document.head.appendChild(styleElement);

// ===== INITIAL LOGO ANIMATION =====
window.addEventListener('load', () => {
    const logo = document.querySelector('.navbar-brand i');
    if (logo) {
        logo.classList.add('animate__animated', 'animate__rubberBand');
        setTimeout(() => {
            logo.classList.remove('animate__rubberBand');
        }, 1000);
    }
    
    // Welcome message
    console.log('%c🚀 System fully loaded and ready!', 'color: #2ec4b6; font-weight: bold;');
});

// ===== SERVICE WORKER REGISTRATION (OPTIONAL) =====
if ('serviceWorker' in navigator && window.location.protocol === 'https:') {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/sw.js').then(registration => {
            console.log('ServiceWorker registered:', registration);
        }).catch(error => {
            console.log('ServiceWorker registration failed:', error);
        });
    });


    
}