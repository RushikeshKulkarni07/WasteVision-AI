const uploadForm = document.getElementById('uploadForm');
const imageInput = document.getElementById('imageInput');
const fileLabel = document.getElementById('fileLabel');
const resultCard = document.getElementById('resultCard');
const resultImage = document.getElementById('resultImage');
const predictedClass = document.getElementById('predictedClass');
const confidenceText = document.getElementById('confidenceText');
const messageBox = document.getElementById('messageBox');
const historyList = document.getElementById('historyList');

imageInput.addEventListener('change', function () {
    const file = this.files[0];
    fileLabel.textContent = file ? file.name : 'Choose an image or drag it here';
});

uploadForm.addEventListener('submit', async function (event) {
    event.preventDefault();

    const file = imageInput.files[0];
    if (!file) {
        showMessage('Please select an image first.', 'error');
        return;
    }

    const formData = new FormData();
    formData.append('image', file);

    showMessage('Classifying image...', 'success');

    try {
        const response = await fetch('/predict', {
            method: 'POST',
            body: formData,
        });

        const data = await response.json();

        if (!response.ok || data.status === 'error') {
            showMessage(data.message || 'Classification failed.', 'error');
            return;
        }

        const objectURL = URL.createObjectURL(file);
        resultImage.src = objectURL;
        resultCard.classList.remove('hidden');
        predictedClass.textContent = data.prediction;
        confidenceText.textContent = `Confidence: ${data.confidence}%`;
        showMessage('Prediction completed successfully.', 'success');
        await loadHistory();
    } catch (error) {
        showMessage('Something went wrong while connecting to the server.', 'error');
    }
});

async function loadHistory() {
    try {
        const response = await fetch('/api/history');
        const data = await response.json();

        if (!response.ok || data.status !== 'success') {
            historyList.innerHTML = '<p>No recent predictions available.</p>';
            return;
        }

        const items = data.history || [];

        if (!items.length) {
            historyList.innerHTML = '<p>No recent predictions available.</p>';
            return;
        }

        historyList.innerHTML = items.map(item => `
            <div class="history-item">
                <strong>${item.class_name}</strong>
                <span>File: ${item.file_name}</span><br>
                <span>Confidence: ${item.confidence}%</span>
            </div>
        `).join('');
    } catch (error) {
        historyList.innerHTML = '<p>History is not available right now.</p>';
    }
}

function showMessage(message, type) {
    messageBox.textContent = message;
    messageBox.className = `message-box ${type}`;
    messageBox.classList.remove('hidden');
}

loadHistory();
