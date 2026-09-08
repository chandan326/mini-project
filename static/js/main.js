document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('feedbackForm');
  if (!form) return;
  let pending = false;
  form.addEventListener('submit', async event => {
    event.preventDefault();
    if (pending) return;
    const data = new FormData(form);
    // FormData(form) omits the clicked submit button, including its true/false value.
    if (event.submitter?.name) data.set(event.submitter.name, event.submitter.value);
    const buttons = [...form.querySelectorAll('button')];
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 20000);
    pending = true; buttons.forEach(button => { button.disabled = true; });
    let error = document.getElementById('feedbackError');
    if (error) error.remove();
    try {
      const response = await fetch(form.action, {method: 'POST', body: data, signal: controller.signal, headers: {'X-Requested-With': 'XMLHttpRequest', 'X-CSRFToken': data.get('csrfmiddlewaretoken')}});
      const result = await response.json();
      if (!response.ok || result.status !== 'success') throw new Error('Unable to save feedback');
      const notice = document.createElement('p'); notice.className = 'alert alert-success mb-0'; notice.setAttribute('role', 'status'); notice.textContent = 'Thank you! Your feedback has been saved.';
      document.getElementById('feedbackContainer').replaceChildren(notice);
    } catch (_) {
      error = document.createElement('p'); error.id = 'feedbackError'; error.className = 'text-danger small'; error.setAttribute('role', 'alert'); error.textContent = 'Feedback could not be saved. Please retry.'; form.append(error);
    } finally { clearTimeout(timeout); pending = false; buttons.forEach(button => { button.disabled = false; }); }
  });
});
