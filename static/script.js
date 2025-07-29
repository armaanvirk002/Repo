// Auto-fill URL when user pastes
document.getElementById('tiktok_url').addEventListener('paste', function(e) {
    setTimeout(() => {
        const url = e.target.value;
        if (url && isValidTikTokURL(url)) {
            e.target.classList.add('border-green-400');
        } else {
            e.target.classList.add('border-red-400');
        }
    }, 100);
});

// URL validation
function isValidTikTokURL(url) {
    const patterns = [
        /https?:\/\/(?:www\.)?tiktok\.com\/@[\w\.-]+\/video\/\d+/,
        /https?:\/\/(?:vm\.)?tiktok\.com\/[\w\.-]+/,
        /https?:\/\/(?:vt\.)?tiktok\.com\/[\w\.-]+/,
        /https?:\/\/(?:www\.)?tiktok\.com\/t\/[\w\.-]+/,
        /https?:\/\/m\.tiktok\.com\/v\/\d+\.html/,
        /https?:\/\/(?:www\.)?tiktok\.com\/.*/,
        /https?:\/\/vm\.tiktok\.com\/.*/,
        /https?:\/\/vt\.tiktok\.com\/.*/
    ];
    
    return patterns.some(pattern => pattern.test(url));
}

// Copy to clipboard function
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(function() {
        // Show success message
        const button = event.target.closest('button');
        const originalText = button.innerHTML;
        button.innerHTML = '<i class="fas fa-check mr-2"></i>Copied!';
        button.classList.add('bg-green-600');
        
        setTimeout(() => {
            button.innerHTML = originalText;
            button.classList.remove('bg-green-600');
        }, 2000);
    }).catch(function(err) {
        console.error('Could not copy text: ', err);
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = text;
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand('copy');
        document.body.removeChild(textArea);
        
        // Show success message
        alert('Link copied to clipboard!');
    });
}

// Show loading indicator on form submit
document.getElementById('urlForm').addEventListener('submit', function() {
    const loading = document.getElementById('loading');
    if (loading) {
        loading.classList.add('active');
    }
});

// URL input validation
document.getElementById('tiktok_url').addEventListener('input', function(e) {
    const url = e.target.value;
    const submitButton = e.target.parentElement.querySelector('button[type="submit"]');
    
    // Always keep the button enabled - let server handle validation
    submitButton.disabled = false;
    submitButton.classList.remove('opacity-50', 'cursor-not-allowed');
    
    if (url && isValidTikTokURL(url)) {
        e.target.classList.remove('border-red-400');
        e.target.classList.add('border-green-400');
    } else if (url) {
        e.target.classList.remove('border-green-400');
        e.target.classList.add('border-red-400');
    } else {
        e.target.classList.remove('border-green-400', 'border-red-400');
    }
});

// Add fade-in animation to elements
document.addEventListener('DOMContentLoaded', function() {
    const elements = document.querySelectorAll('.glass');
    elements.forEach((el, index) => {
        setTimeout(() => {
            el.classList.add('fade-in');
        }, index * 100);
    });
    
    // Ensure submit button is always clickable on page load
    const submitButton = document.querySelector('button[type="submit"]');
    if (submitButton) {
        submitButton.disabled = false;
        submitButton.classList.remove('opacity-50', 'cursor-not-allowed');
    }
});

// Download function with progress animation and direct download
async function startDownload(format, url) {
    const progressDiv = document.getElementById('downloadProgress');
    const progressBar = document.getElementById('progressBar');
    const progressText = document.getElementById('progressText');
    const progressPercent = document.getElementById('progressPercent');
    const downloadBtns = document.querySelectorAll('.download-btn');
    
    // Disable all download buttons
    downloadBtns.forEach(btn => {
        btn.disabled = true;
        btn.classList.add('opacity-50', 'cursor-not-allowed');
    });
    
    // Show progress bar
    progressDiv.classList.remove('hidden');
    
    // Animate progress
    let progress = 0;
    const progressMessages = [
        'Preparing download...',
        'Processing TikTok video...',
        'Extracting content...',
        'Optimizing quality...',
        'Finalizing download...'
    ];
    
    const progressInterval = setInterval(() => {
        progress += Math.random() * 15 + 5; // Random increment between 5-20%
        if (progress > 85) progress = 85; // Stop at 85% until actual download
        
        progressBar.style.width = progress + '%';
        progressPercent.textContent = Math.round(progress) + '%';
        
        // Update message based on progress
        const messageIndex = Math.floor(progress / 20);
        if (messageIndex < progressMessages.length) {
            progressText.textContent = progressMessages[messageIndex];
        }
    }, 200);
    
    try {
        // Start actual download using fetch
        const downloadUrl = `/download/${format}?url=${url}`;
        const response = await fetch(downloadUrl);
        
        if (!response.ok) {
            throw new Error(`Download failed: ${response.statusText}`);
        }
        
        // Complete progress animation
        clearInterval(progressInterval);
        progress = 95;
        progressBar.style.width = '95%';
        progressPercent.textContent = '95%';
        progressText.textContent = 'Downloading file...';
        
        // Get the file as blob
        const blob = await response.blob();
        
        // Complete progress
        progress = 100;
        progressBar.style.width = '100%';
        progressPercent.textContent = '100%';
        progressText.textContent = 'Download completed!';
        
        // Extract filename from Content-Disposition header or use default
        let filename = `tiktok_${format === 'mp4' ? 'video' : 'audio'}.${format}`;
        const contentDisposition = response.headers.get('Content-Disposition');
        if (contentDisposition) {
            const filenameMatch = contentDisposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/);
            if (filenameMatch && filenameMatch[1]) {
                filename = filenameMatch[1].replace(/['"]/g, '');
            }
        }
        
        // Create download link and trigger download directly
        const downloadLink = document.createElement('a');
        downloadLink.href = URL.createObjectURL(blob);
        downloadLink.download = filename;
        downloadLink.style.display = 'none';
        
        // Add to DOM, click, and remove immediately
        document.body.appendChild(downloadLink);
        downloadLink.click();
        
        // Clean up immediately
        setTimeout(() => {
            document.body.removeChild(downloadLink);
            URL.revokeObjectURL(downloadLink.href);
        }, 100);
        
    } catch (error) {
        clearInterval(progressInterval);
        progressBar.style.width = '100%';
        progressBar.classList.add('bg-red-500');
        progressPercent.textContent = 'Error';
        progressText.textContent = 'Download failed. Please try again.';
        console.error('Download error:', error);
    }
    
    // Hide progress after 2 seconds
    setTimeout(() => {
        progressDiv.classList.add('hidden');
        progressBar.style.width = '0%';
        progressBar.classList.remove('bg-red-500');
        progressPercent.textContent = '0%';
        progressText.textContent = 'Preparing download...';
        
        // Re-enable buttons
        downloadBtns.forEach(btn => {
            btn.disabled = false;
            btn.classList.remove('opacity-50', 'cursor-not-allowed');
        });
    }, 2000);
}
