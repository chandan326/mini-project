/**
 * AgriHealth AI - General Scripts & Feedback Handler
 */

document.addEventListener('DOMContentLoaded', function () {
  // Feedback Ajax Submission
  const feedbackForm = document.getElementById('feedbackForm');
  if (feedbackForm) {
    feedbackForm.addEventListener('submit', function (e) {
      e.preventDefault();
      const formData = new FormData(feedbackForm);
      const actionUrl = feedbackForm.getAttribute('action');

      fetch(actionUrl, {
        method: 'POST',
        headers: {
          'X-Requested-With': 'XMLHttpRequest',
          'X-CSRFToken': formData.get('csrfmiddlewaretoken')
        },
        body: formData
      })
        .then(response => response.json())
        .then(data => {
          const feedbackContainer = document.getElementById('feedbackContainer');
          if (feedbackContainer) {
            feedbackContainer.innerHTML = `
            <div class="alert alert-success d-flex align-items-center gap-2 mb-0" role="alert">
              <i class="fas fa-check-circle fa-lg"></i>
              <div>Thank you! Your feedback helps train and improve our agricultural AI model.</div>
            </div>
          `;
          }
        })
        .catch(err => {
          feedbackForm.submit();
        });
    });
  }
});
