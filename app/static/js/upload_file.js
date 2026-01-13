document.getElementById('uploadForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const fileInput = document.getElementById('fileInput');
    const formData = new FormData();

    for (const file of fileInput.files) {
        formData.append('files', file);
    }

    try {
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (response.ok) {
            document.getElementById('results').style.display = 'block';
            document.getElementById('jsonOutput').textContent = JSON.stringify(data, null, 2);
        } else {
            alert('Error: ' + (data.error || 'Upload failed'));
        }
    } catch (error) {
        alert('Upload failed: ' + error.message);
    }
});