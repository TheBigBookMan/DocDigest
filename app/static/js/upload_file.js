let failedFiles = [];

document.addEventListener('DOMContentLoaded', () => {
    const tabButtons = document.querySelectorAll('.tab-button');
    
    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            const tabName = button.getAttribute('data-tab');
            
            tabButtons.forEach(btn => btn.classList.remove('active'));
            document.querySelectorAll('.tab-panel').forEach(panel => {
                panel.classList.remove('active');
            });
            
            button.classList.add('active');
            document.getElementById(`${tabName}-tab`).classList.add('active');
        });
    });
});

document.getElementById('uploadForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const fileInput = document.getElementById('fileInput');
    const emailInput = document.getElementById('email');
    const errorMessage = document.getElementById('errorMessage');
    const fileStatusSection = document.getElementById('fileStatusSection');
    
    errorMessage.style.display = 'none';
    errorMessage.textContent = '';
    document.getElementById('results').style.display = 'none';

    const formData = new FormData();
    formData.append('email', emailInput.value);

    const allFiles = [];
    for (const file of fileInput.files) {
        formData.append('files', file);
        allFiles.push(file.name);
    }

    try {
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (response.ok && data.status === 'success') {
            fileStatusSection.style.display = 'block';
            
            const uploadedFiles = data.uploaded_files || [];
            const canceledFileNames = allFiles.filter(file => !uploadedFiles.includes(file));
            
            failedFiles = Array.from(fileInput.files).filter(file =>
                canceledFileNames.includes(file.name)
            );
            
            updateProcessingTab(uploadedFiles);
            updateCanceledTab(canceledFileNames);
            
            document.getElementById('processingCount').textContent = uploadedFiles.length;
            document.getElementById('canceledCount').textContent = canceledFileNames.length;
            
        } else {
            errorMessage.textContent = data.error || 'Upload failed';
            errorMessage.style.display = 'block';
        }
    } catch (error) {
        errorMessage.textContent = 'Upload failed: ' + error.message;
        errorMessage.style.display = 'block';
    }
});

function updateProcessingTab(files) {
    const processingContainer = document.getElementById('processingFiles');
    processingContainer.innerHTML = '';
    
    if (files.length === 0) {
        processingContainer.innerHTML = '<p class="empty-state">No files processing</p>';
        return;
    }
    
    files.forEach(filename => {
        const fileItem = document.createElement('div');
        fileItem.className = 'file-item processing';
        fileItem.innerHTML = `
            <div class="spinner"></div>
            <span class="file-name">${filename}</span>
            <span class="file-status">Processing...</span>
        `;
        processingContainer.appendChild(fileItem);
    });
}

function updateCanceledTab(files) {
    const canceledContainer = document.getElementById('canceledFiles');
    canceledContainer.innerHTML = '';
    
    if (files.length === 0) {
        canceledContainer.innerHTML = '<p class="empty-state">No failed uploads</p>';
        return;
    }
    
    files.forEach(filename => {
        const fileItem = document.createElement('div');
        fileItem.className = 'file-item canceled';
        fileItem.innerHTML = `
            <span class="file-name">${filename}</span>
            <span class="file-status">Failed</span>
            <button class="retry-button" onclick="retryUpload('${filename}')">
                <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                    <path d="M14 8C14 11.3137 11.3137 14 8 14C4.68629 14 2 11.3137 2 8C2 4.68629 4.68629 2 8 2C9.84871 2 11.5 2.82872 12.6 4.2M12.6 4.2V2M12.6 4.2H10.4" 
                          stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
                Retry
            </button>
        `;
        canceledContainer.appendChild(fileItem);
    });
}

async function retryUpload(filename) {
    const fileToRetry = failedFiles.find(file => file.name === filename);
    
    if (!fileToRetry) {
        alert('File not found for retry');
        return;
    }
    
    const emailInput = document.getElementById('email');
    const formData = new FormData();
    formData.append('email', emailInput.value);
    formData.append('files', fileToRetry);
    
    const retryButton = event.target.closest('.retry-button');
    const originalHTML = retryButton.innerHTML;
    retryButton.disabled = true;
    retryButton.innerHTML = '<div class="spinner small"></div> Retrying...';
    
    try {
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (response.ok && data.status === 'success' && data.uploaded_files.includes(filename)) {
            const canceledFiles = Array.from(document.querySelectorAll('#canceledFiles .file-item'))
                .map(item => item.querySelector('.file-name').textContent)
                .filter(name => name !== filename);
            
            const processingFiles = Array.from(document.querySelectorAll('#processingFiles .file-item'))
                .map(item => item.querySelector('.file-name').textContent);
            processingFiles.push(filename);
            
            failedFiles = failedFiles.filter(file => file.name !== filename);
            
            updateProcessingTab(processingFiles);
            updateCanceledTab(canceledFiles);
            
            document.getElementById('processingCount').textContent = processingFiles.length;
            document.getElementById('canceledCount').textContent = canceledFiles.length;
            
        } else {
            alert('Retry failed: ' + (data.error || 'Unknown error'));
            retryButton.disabled = false;
            retryButton.innerHTML = originalHTML;
        }
    } catch (error) {
        alert('Retry failed: ' + error.message);
        retryButton.disabled = false;
        retryButton.innerHTML = originalHTML;
    }
}