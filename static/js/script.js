document.getElementById('qa-form').addEventListener('submit', async function(event) {
  event.preventDefault();

  const formData = new FormData();
  const questionImage = document.getElementById('question-image').files[0];
  const answerImage = document.getElementById('answer-image').files[0];
  const classLevel = document.getElementById('class').value;
  const board = document.getElementById('board').value;
  const questionType = document.getElementById('question-type').value;

  formData.append('question_image', questionImage);
  formData.append('answer_image', answerImage);
  formData.append('class', classLevel);
  formData.append('board', board);
  formData.append('question_type', questionType);

  try {
    const response = await fetch('/upload', {
      method: 'POST',
      body: formData
    });

    const result = await response.json();

    const outputArea = document.getElementById('output-area');
    const serverResponse = document.getElementById('server-response');
    serverResponse.innerHTML = `
        <p><strong>Feedback:</strong> ${result.Feedback}</p>
        <p><strong>Score:</strong> ${result.Score}</p>
    `;
    outputArea.style.display = 'block';
  } catch (error) {
    const outputArea = document.getElementById('output-area');
    const serverResponse = document.getElementById('server-response');

    serverResponse.textContent = "An error occurred: " + error.message;
    outputArea.style.display = 'block'
  }
});
