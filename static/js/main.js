// Main JavaScript for the Multi-Agent SEO Blog Generator

document.addEventListener('DOMContentLoaded', function() {
    // Initialize feather icons
    feather.replace();
    
    // Get form and progress elements
    const blogForm = document.getElementById('blog-form');
    const progressContainer = document.getElementById('progress-container');
    const progressBar = document.getElementById('progress-bar');
    const progressStatus = document.getElementById('progress-status');
    const progressMessage = document.getElementById('progress-message');
    
    // If on the form page with progress monitoring
    if (blogForm && progressContainer) {
        blogForm.addEventListener('submit', function(e) {
            // Show progress container
            progressContainer.classList.remove('d-none');
            
            // Start progress polling
            pollProgress();
        });
    }
    
    // Function to poll progress
    function pollProgress() {
        const progressInterval = setInterval(function() {
            fetch('/progress')
                .then(response => response.json())
                .then(data => {
                    // Update progress UI
                    progressBar.style.width = data.completion + '%';
                    progressBar.setAttribute('aria-valuenow', data.completion);
                    progressMessage.textContent = data.message;
                    
                    // Update status based on completion
                    if (data.status === 'complete') {
                        progressStatus.textContent = 'Blog Post Complete!';
                        progressBar.classList.remove('progress-bar-animated');
                        progressBar.classList.add('bg-success');
                        clearInterval(progressInterval);
                    } else if (data.status === 'error') {
                        progressStatus.textContent = 'Error';
                        progressBar.classList.remove('progress-bar-animated');
                        progressBar.classList.add('bg-danger');
                        clearInterval(progressInterval);
                    } else {
                        // Set status based on current stage
                        const statusMap = {
                            'researching': 'Research Agent Working...',
                            'planning': 'Planning Agent Working...',
                            'writing': 'Content Generation In Progress...',
                            'optimizing': 'SEO Optimization In Progress...',
                            'reviewing': 'Review Agent Working...'
                        };
                        
                        progressStatus.textContent = statusMap[data.status] || 'Processing...';
                    }
                })
                .catch(error => {
                    console.error('Error checking progress:', error);
                });
        }, 2000); // Poll every 2 seconds
    }
    
    // Theme toggling functionality (if implemented)
    const themeToggle = document.getElementById('theme-toggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', function() {
            const html = document.querySelector('html');
            if (html.getAttribute('data-bs-theme') === 'dark') {
                html.setAttribute('data-bs-theme', 'light');
                themeToggle.innerHTML = '<i data-feather="moon"></i>';
            } else {
                html.setAttribute('data-bs-theme', 'dark');
                themeToggle.innerHTML = '<i data-feather="sun"></i>';
            }
            feather.replace();
        });
    }
});
