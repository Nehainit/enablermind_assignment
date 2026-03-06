// EnableMind Web UI - Client-side JavaScript

// Form validation for research submission
document.addEventListener('DOMContentLoaded', function() {
    const researchForm = document.querySelector('form[action="/research"]');

    if (researchForm) {
        researchForm.addEventListener('submit', function(e) {
            const topicInput = document.getElementById('topic');
            const topic = topicInput.value.trim();

            // Validate topic
            if (!topic) {
                e.preventDefault();
                alert('Please enter a research topic');
                topicInput.focus();
                return false;
            }

            if (topic.length > 500) {
                e.preventDefault();
                alert('Topic is too long (max 500 characters)');
                topicInput.focus();
                return false;
            }

            // Show loading state on submit button
            const submitButton = researchForm.querySelector('button[type="submit"]');
            if (submitButton) {
                submitButton.disabled = true;
                submitButton.innerHTML = `
                    <svg class="animate-spin w-5 h-5 mr-2 inline" fill="none" viewBox="0 0 24 24">
                        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Starting Research...
                `;
            }
        });
    }
});

// Character counter for topic textarea
document.addEventListener('DOMContentLoaded', function() {
    const topicTextarea = document.getElementById('topic');

    if (topicTextarea) {
        const maxLength = 500;
        const counterDiv = document.createElement('div');
        counterDiv.className = 'text-xs text-gray-500 mt-1 text-right';
        topicTextarea.parentElement.appendChild(counterDiv);

        function updateCounter() {
            const remaining = maxLength - topicTextarea.value.length;
            counterDiv.textContent = `${remaining} characters remaining`;

            if (remaining < 50) {
                counterDiv.className = 'text-xs text-orange-500 mt-1 text-right';
            } else if (remaining < 0) {
                counterDiv.className = 'text-xs text-red-500 mt-1 text-right font-medium';
            } else {
                counterDiv.className = 'text-xs text-gray-500 mt-1 text-right';
            }
        }

        topicTextarea.addEventListener('input', updateCounter);
        updateCounter(); // Initial update
    }
});

// Auto-focus on topic input
document.addEventListener('DOMContentLoaded', function() {
    const topicInput = document.getElementById('topic');
    if (topicInput && window.location.pathname === '/') {
        topicInput.focus();
    }
});

// Handle HTMX errors gracefully
document.body.addEventListener('htmx:responseError', function(event) {
    console.error('HTMX request failed:', event.detail);

    // Show user-friendly error message
    const errorDiv = document.createElement('div');
    errorDiv.className = 'fixed top-4 right-4 bg-red-50 border-l-4 border-red-400 p-4 shadow-lg rounded z-50';
    errorDiv.innerHTML = `
        <div class="flex">
            <div class="flex-shrink-0">
                <svg class="h-5 w-5 text-red-400" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
                </svg>
            </div>
            <div class="ml-3">
                <p class="text-sm text-red-700">Failed to load data. Please refresh the page.</p>
            </div>
            <button onclick="this.parentElement.parentElement.remove()" class="ml-auto">
                <svg class="h-5 w-5 text-red-400" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
                </svg>
            </button>
        </div>
    `;
    document.body.appendChild(errorDiv);

    // Auto-remove after 5 seconds
    setTimeout(() => errorDiv.remove(), 5000);
});

// Log HTMX activity in development
if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
    document.body.addEventListener('htmx:beforeRequest', function(event) {
        console.log('HTMX Request:', event.detail.path);
    });

    document.body.addEventListener('htmx:afterSwap', function(event) {
        console.log('HTMX Swap Complete:', event.detail.target.id);
    });
}
