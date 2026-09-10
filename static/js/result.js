document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('[data-result-photo]').forEach(card => {
    const image = card.querySelector('img');
    const message = card.querySelector('.photo-load-error');
    const retry = card.querySelector('[data-retry-photo]');
    const source = image.getAttribute('src');
    function settle(failed) {
      image.hidden = failed;
      message.hidden = !failed;
      retry.disabled = false;
      card.removeAttribute('aria-busy');
    }
    image.addEventListener('load', () => settle(false));
    image.addEventListener('error', () => settle(true));
    if (image.complete) settle(image.naturalWidth === 0);
    retry.addEventListener('click', () => {
      retry.disabled = true;
      card.setAttribute('aria-busy', 'true');
      const url = new URL(source, location.href);
      url.searchParams.set('retry', Date.now());
      image.src = url.href;
    });
  });
});
