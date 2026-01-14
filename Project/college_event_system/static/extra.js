// Show toast notification
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    document.body.appendChild(toast);
    
    setTimeout(() => toast.classList.add('show'), 100);
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// Form validation
document.querySelectorAll('form').forEach(form => {
    form.addEventListener('submit', function(e) {
        const inputs = this.querySelectorAll('input[required]');
        let valid = true;
        
        inputs.forEach(input => {
            if (!input.value.trim()) {
                input.style.borderColor = 'red';
                valid = false;
                showToast('Please fill all required fields', 'error');
            } else {
                input.style.borderColor = '';
            }
        });
        
        if (!valid) {
            e.preventDefault();
        }
    });
});

// QR Scanner simulation
const qrBtn = document.querySelector('.btn-primary');
if (qrBtn && qrBtn.textContent.includes('Camera')) {
    qrBtn.addEventListener('click', function() {
        this.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Scanning...';
        this.disabled = true;
        
        setTimeout(() => {
            showToast('Attendance marked successfully!', 'success');
            this.innerHTML = '<i class="fas fa-check"></i> Attendance Marked';
            this.classList.remove('btn-primary');
            this.classList.add('btn-success');
        }, 2000);
    });
}