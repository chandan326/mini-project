document.addEventListener('DOMContentLoaded', () => {
  const dialog = document.getElementById('tutorialDialog');
  const video = document.getElementById('tutorialVideo');
  if (!dialog || !video || typeof dialog.showModal !== 'function') return;
  const play = document.getElementById('tutorialPlay');
  const status = document.getElementById('tutorialStatus');
  let opener;
  const start = () => {
    status.textContent = '';
    const promise = video.play();
    if (promise) promise.catch(() => {
      if (dialog.open) status.textContent = 'Press Play to start. If playback fails, download the MP4 or read the transcript.';
    });
  };
  document.querySelectorAll('[data-tutorial-open]').forEach(link => {
    link.addEventListener('click', event => {
      // Preserve open-in-new-tab behaviour and the no-JavaScript guide link.
      if (event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
      event.preventDefault(); opener = link;
      if (!dialog.open) dialog.showModal();
      document.body.classList.add('tutorial-open');
      if (!video.hasAttribute('src')) { video.src = video.dataset.src; video.load(); }
      start();
    });
  });
  const close = () => { if (dialog.open) dialog.close(); };
  dialog.querySelectorAll('[data-tutorial-close]').forEach(button => button.addEventListener('click', close));
  dialog.addEventListener('click', event => { if (event.target === dialog) {
    const bounds = dialog.getBoundingClientRect();
    if (event.clientX < bounds.left || event.clientX > bounds.right || event.clientY < bounds.top || event.clientY > bounds.bottom) close();
  } });
  dialog.addEventListener('close', () => {
    video.pause(); video.currentTime = 0;
    document.body.classList.remove('tutorial-open');
    opener?.focus({preventScroll: true});
  });
  play.addEventListener('click', () => { if (video.paused) start(); else video.pause(); });
  ['play', 'pause', 'ended'].forEach(name => video.addEventListener(name, () => { play.textContent = video.paused ? 'Play' : 'Pause'; }));
  document.getElementById('tutorialReplay').addEventListener('click', () => { video.currentTime = 0; start(); });
  dialog.querySelectorAll('[data-tutorial-seek]').forEach(button => button.addEventListener('click', () => {
    if (Number.isFinite(video.duration)) video.currentTime = Math.min(video.duration, Math.max(0, video.currentTime + Number(button.dataset.tutorialSeek)));
  }));
  document.getElementById('tutorialSpeed').addEventListener('change', event => { video.playbackRate = Number(event.target.value); });
  video.addEventListener('error', () => { status.textContent = 'The video could not load. Please retry, download the MP4, or read the transcript below.'; });
  document.addEventListener('visibilitychange', () => { if (document.hidden) video.pause(); });
  window.addEventListener('pagehide', () => video.pause());
});
