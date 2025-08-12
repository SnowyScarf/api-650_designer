/**
 * Acetic Acid Storage Tank Design Tool
 * Client-side JavaScript for enhanced user interaction
 */

document.addEventListener('DOMContentLoaded', function() {
    
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Form validation enhancement
    const forms = document.querySelectorAll('.needs-validation');
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            } else {
                // Add loading state to submit button
                const submitBtn = form.querySelector('button[type="submit"]');
                if (submitBtn) {
                    submitBtn.classList.add('btn-loading');
                    submitBtn.disabled = true;
                    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Calculating...';
                }
            }
            form.classList.add('was-validated');
        });
    });

    // Real-time input validation feedback
    const inputs = document.querySelectorAll('input[type="number"]');
    inputs.forEach(input => {
        input.addEventListener('input', function() {
            if (this.value && this.checkValidity()) {
                this.classList.remove('is-invalid');
                this.classList.add('is-valid');
            } else if (this.value) {
                this.classList.remove('is-valid');
                this.classList.add('is-invalid');
            } else {
                this.classList.remove('is-valid', 'is-invalid');
            }
        });
    });

    // Calculate derived values on input change
    const productionRateInput = document.getElementById('production_rate');
    const holdingPeriodInput = document.getElementById('holding_period');
    const densityInput = document.getElementById('density');

    if (productionRateInput && holdingPeriodInput && densityInput) {
        [productionRateInput, holdingPeriodInput, densityInput].forEach(input => {
            input.addEventListener('input', updatePreview);
        });
    }

    function updatePreview() {
        const productionRate = parseFloat(productionRateInput.value) || 0;
        const holdingPeriod = parseFloat(holdingPeriodInput.value) || 0;
        const density = parseFloat(densityInput.value) || 1049;

        if (productionRate > 0 && holdingPeriod > 0) {
            const totalMass = productionRate * holdingPeriod;
            const totalVolume = (totalMass * 1000) / density;
            
            // Show preview if elements exist
            const previewElement = document.getElementById('volume-preview');
            if (previewElement) {
                previewElement.innerHTML = `
                    <small class="text-muted">
                        Preview: ${totalMass.toFixed(1)} tonnes → ${totalVolume.toFixed(1)} m³ total storage
                    </small>
                `;
            }
        }
    }

    // Smooth scroll to results
    const resultsSection = document.querySelector('.container.my-5');
    if (resultsSection && window.location.pathname.includes('results')) {
        setTimeout(() => {
            resultsSection.scrollIntoView({ behavior: 'smooth' });
        }, 100);
    }

    // Print functionality enhancement
    window.printResults = function() {
        // Hide non-essential elements for printing
        const elementsToHide = document.querySelectorAll('.btn, .navbar, .alert');
        elementsToHide.forEach(el => el.style.display = 'none');
        
        window.print();
        
        // Restore elements after printing
        setTimeout(() => {
            elementsToHide.forEach(el => el.style.display = '');
        }, 1000);
    };

    // Enhanced chart interactions
    if (typeof Plotly !== 'undefined' && document.getElementById('thicknessChart')) {
        // Add custom hover template
        document.getElementById('thicknessChart').on('plotly_hover', function(data) {
            const point = data.points[0];
            const customTooltip = `
                <div class="custom-tooltip">
                    <strong>Height:</strong> ${point.x} m<br>
                    <strong>Thickness:</strong> ${point.y} mm
                </div>
            `;
            // Could implement custom tooltip if needed
        });
    }

    // Animate cards on scroll
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in-up');
            }
        });
    }, observerOptions);

    // Observe all cards
    document.querySelectorAll('.card').forEach(card => {
        observer.observe(card);
    });

    // Auto-save form data to localStorage
    const form = document.querySelector('form');
    if (form) {
        // Load saved data
        const savedData = localStorage.getItem('tankDesignForm');
        if (savedData) {
            const data = JSON.parse(savedData);
            Object.keys(data).forEach(key => {
                const input = form.querySelector(`[name="${key}"]`);
                if (input && !input.value) {
                    input.value = data[key];
                }
            });
        }

        // Save data on change
        form.addEventListener('input', function() {
            const formData = new FormData(form);
            const data = {};
            for (let [key, value] of formData.entries()) {
                data[key] = value;
            }
            localStorage.setItem('tankDesignForm', JSON.stringify(data));
        });
    }

    // Clear saved form data when calculation is successful
    if (window.location.pathname.includes('results')) {
        localStorage.removeItem('tankDesignForm');
    }

    // Export button enhancements
    const exportButtons = document.querySelectorAll('a[href*="export"]');
    exportButtons.forEach(button => {
        button.addEventListener('click', function() {
            const originalText = this.innerHTML;
            this.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Generating...';
            this.classList.add('disabled');
            
            setTimeout(() => {
                this.innerHTML = originalText;
                this.classList.remove('disabled');
            }, 3000);
        });
    });

    // Add keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + Enter to submit form
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
            const form = document.querySelector('form');
            if (form) {
                form.requestSubmit();
            }
        }
        
        // Escape to clear form
        if (e.key === 'Escape') {
            const form = document.querySelector('form');
            if (form) {
                const resetBtn = form.querySelector('button[type="reset"]');
                if (resetBtn) {
                    resetBtn.click();
                }
            }
        }
    });

    // Add confirmation for form reset
    const resetButton = document.querySelector('button[type="reset"]');
    if (resetButton) {
        resetButton.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to reset all form fields?')) {
                e.preventDefault();
            } else {
                localStorage.removeItem('tankDesignForm');
            }
        });
    }

    console.log('Acetic Acid Tank Design Tool initialized successfully');
});

// Utility functions
function formatNumber(num, decimals = 2) {
    return parseFloat(num).toFixed(decimals);
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    notification.style.top = '20px';
    notification.style.right = '20px';
    notification.style.zIndex = '9999';
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        if (notification.parentNode) {
            notification.parentNode.removeChild(notification);
        }
    }, 5000);
}

// Export for use in other scripts
window.TankDesignTool = {
    formatNumber,
    showNotification
};
