document.getElementById('qa-form').addEventListener('submit', async function(event) {
  event.preventDefault();

  const formData = new FormData();
  const answerImage = document.getElementById('answer-image').files[0];
  formData.append('answer_image', answerImage);

  const progressBarContainer = document.getElementById('progress-bar-container');
  const progressBar = document.getElementById('progress-bar');

  // Show the progress bar
  progressBarContainer.style.display = 'block';
  progressBar.style.width = '0%';

  // Simulate progress
  let progress = 0;
  const progressInterval = setInterval(() => {
    progress = Math.min(progress + 10, 90); // Stop at 90% while waiting for response
    progressBar.style.width = `${progress}%`;
  }, 500);

  try {
    const response = await fetch('/upload', {
      method: 'POST',
      body: formData
    });

    clearInterval(progressInterval); // Stop the progress interval
    progressBar.style.width = '100%'; // Complete the progress bar

    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }

    const result = await response.json();

    // Display Evaluation Feedback and Score
    const outputArea = document.getElementById('output-area');
    const serverResponse = document.getElementById('server-response');
    serverResponse.innerHTML = `
        <p><strong>Feedback:</strong> ${result.Feedback}</p>
        <p><strong>Score:</strong> ${result.Score}</p>
    `;
    outputArea.style.display = 'block';

    // Display Extracted Text
    const textOutputArea = document.getElementById('text-output-area');
    const extractedText = document.getElementById('extracted-text');
    extractedText.textContent = result.ExtractedText || 'No text was extracted.';
    textOutputArea.style.display = 'block';
  } catch (error) {
    // Handle errors
    clearInterval(progressInterval);
    const outputArea = document.getElementById('output-area');
    const serverResponse = document.getElementById('server-response');

    serverResponse.textContent = "An error occurred: " + error.message;
    outputArea.style.display = 'block';
  } finally {
    setTimeout(() => {
      progressBarContainer.style.display = 'none';
    }, 1000);
  }
});
