document.getElementById('uploadForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const fileInput = document.getElementById('fileInput');
    const emailInput = document.getElementById('email');
    const errorMessage = document.getElementById('errorMessage');

    errorMessage.style.display = 'none';
    errorMessage.textContent = '';

    const formData = new FormData();
    formData.append('email', emailInput.value);

    for (const file of fileInput.files) {
        formData.append('files', file);
    }

    try {
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();
        console.log(response);
        console.log(data);

        if (response.ok) {
            if (data.status === 'success') {
                document.getElementById('results').style.display = 'block';
                document.getElementById('jsonOutput').textContent = JSON.stringify(data, null, 2);
            } else if (data.status === 'error') {
                errorMessage.textContent = data.error || 'An error occurred';
                errorMessage.style.display = 'block';
            }
        } else {
            errorMessage.textContent = data.error || 'Upload failed';
            errorMessage.style.display = 'block';
        }
    } catch (error) {
        errorMessage.textContent = 'Upload failed: ' + error.message;
        errorMessage.style.display = 'block';
    }
});