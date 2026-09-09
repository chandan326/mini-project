/* Plant photo workflow: additive uploads, bounded image processing and real request progress. */
document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('diagnosisWizardForm');
  if (!form) return;
  const $ = id => document.getElementById(id);
  const panes = [$('step-1-crop'), $('step-2-photos'), $('step-3-questions'), $('step-4-loading')];
  const cards = [...document.querySelectorAll('.crop-select-card')];
  const photos = [];
  let step = 1, preparing = false, submitting = false, stream = null, cameraGeneration = 0, facing = 'environment';
  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  function showError(message) {
    $('wizardError').textContent = message;
    $('wizardError').hidden = !message;
    if (message) $('wizardError').focus({preventScroll: true});
  }
  function selectCrop(card) {
    cards.forEach(item => { item.classList.toggle('selected', item === card); item.setAttribute('aria-pressed', String(item === card)); });
    $('selected_crop_id').value = card.dataset.cropId;
    showError('');
  }
  cards.forEach(card => card.addEventListener('click', () => { selectCrop(card); goToStep(2); }));
  const preselected = cards.find(card => card.dataset.cropId === new URLSearchParams(location.search).get('crop'));
  if (preselected) selectCrop(preselected);
  $('cropSearchInput').addEventListener('input', event => {
    const query = event.target.value.trim().toLocaleLowerCase();
    cards.forEach(card => { card.parentElement.hidden = !card.textContent.toLocaleLowerCase().includes(query); });
  });
  function updateControls() {
    const busy = preparing || submitting;
    ['choosePhotos', 'takePhoto', 'nativeCamera'].forEach(id => { $(id).disabled = busy || photos.length >= 5; });
    $('btn-next').disabled = busy;
    $('btn-prev').disabled = busy;
    $('btn-submit').disabled = busy;
    $('capturePhoto').disabled = busy || !stream || photos.length >= 5;
    $('photoCount').textContent = `${photos.length} / 5 photos`;
    $('photoEmpty').hidden = photos.length > 0;
    $('photoGrid').querySelectorAll('button').forEach(button => { button.disabled = busy; });
  }
  function renderPhotos() {
    $('photoGrid').replaceChildren();
    photos.forEach((photo, index) => {
      const card = document.createElement('div'); card.className = 'photo-card';
      const img = document.createElement('img'); img.src = photo.url; img.alt = `Plant photo ${index + 1}`; img.decoding = 'async';
      const caption = document.createElement('span'); caption.className = 'photo-caption'; caption.textContent = `Photo ${index + 1} · ${Math.ceil(photo.file.size / 1024)} KB`;
      const remove = document.createElement('button'); remove.type = 'button'; remove.className = 'photo-remove'; remove.textContent = '×';
      remove.setAttribute('aria-label', `Remove photo ${index + 1}`);
      remove.addEventListener('click', () => { URL.revokeObjectURL(photo.url); photos.splice(index, 1); renderPhotos(); showError(''); });
      card.append(img, caption, remove); $('photoGrid').append(card);
    });
    updateControls();
  }
  async function optimize(file) {
    if (!['image/jpeg', 'image/png', 'image/webp'].includes(file.type)) throw new Error('Choose JPG, PNG or WebP. Convert HEIC photos to JPG first.');
    if (file.size > 20 * 1024 * 1024) throw new Error('Each original photo must be below 20 MB.');
    let source, sourceUrl;
    try {
      if ('createImageBitmap' in window) source = await createImageBitmap(file, {imageOrientation: 'from-image'});
      else {
        sourceUrl = URL.createObjectURL(file); source = new Image(); source.src = sourceUrl; await source.decode();
      }
      const width = source.width || source.naturalWidth, height = source.height || source.naturalHeight;
      if (Math.min(width, height) < 200) throw new Error('Use a clearer photo of at least 200 × 200 pixels.');
      if (width * height > 30000000) throw new Error('Photo resolution is too large. Please resize it first.');
      const canvas = document.createElement('canvas');
      const scale = Math.min(1, 1600 / Math.max(width, height));
      canvas.width = Math.round(width * scale); canvas.height = Math.round(height * scale);
      const context = canvas.getContext('2d'); context.fillStyle = '#fff'; context.fillRect(0, 0, canvas.width, canvas.height);
      context.drawImage(source, 0, 0, canvas.width, canvas.height);
      let blob;
      for (const quality of [0.86, 0.75, 0.62, 0.5]) {
        blob = await new Promise(resolve => canvas.toBlob(resolve, 'image/jpeg', quality));
        if (blob && blob.size <= 650000) break;
      }
      if (!blob || blob.size > 650000) throw new Error('This photo is too detailed to optimize. Please choose a smaller image.');
      return new File([blob], `plant-${Date.now()}-${Math.random().toString(36).slice(2, 7)}.jpg`, {type: 'image/jpeg'});
    } catch (error) {
      if (error.name === 'InvalidStateError' || error.name === 'EncodingError') throw new Error('This file could not be read. Choose another plant photo.');
      throw error;
    } finally {
      if (source?.close) source.close();
      if (sourceUrl) URL.revokeObjectURL(sourceUrl);
    }
  }
  async function addPhotos(files) {
    if (preparing || submitting || !files.length) return;
    if (photos.length + files.length > 5) { showError(`You can add ${5 - photos.length} more photo(s), up to 5 total.`); return; }
    preparing = true; updateControls(); showError('');
    const errors = [];
    for (const [index, original] of [...files].entries()) {
      $('photoStatus').textContent = `Preparing photo ${index + 1} of ${files.length}…`;
      const fingerprint = `${original.name}:${original.size}:${original.lastModified}`;
      if (photos.some(photo => photo.fingerprint === fingerprint)) { errors.push('That photo is already selected.'); continue; }
      try {
        const file = await optimize(original);
        photos.push({file, fingerprint, url: URL.createObjectURL(file)});
        renderPhotos();
      } catch (error) { errors.push(error.message); }
    }
    preparing = false; renderPhotos();
    $('photoStatus').textContent = photos.length ? 'Photos ready. Remove a photo to replace it.' : '';
    if (errors.length) showError([...new Set(errors)].join(' '));
    if (photos.length === 5 && $('cameraDialog').open) closeCamera();
  }
  $('choosePhotos').addEventListener('click', () => $('galleryInput').click());
  $('galleryInput').addEventListener('change', event => { addPhotos([...event.target.files]); event.target.value = ''; });
  $('nativeCameraInput').addEventListener('change', event => { addPhotos([...event.target.files]); event.target.value = ''; });
  ['dragenter', 'dragover'].forEach(type => $('photoDropZone').addEventListener(type, event => { event.preventDefault(); $('photoDropZone').classList.add('dragging'); }));
  ['dragleave', 'drop'].forEach(type => $('photoDropZone').addEventListener(type, event => { event.preventDefault(); $('photoDropZone').classList.remove('dragging'); }));
  $('photoDropZone').addEventListener('drop', event => addPhotos([...event.dataTransfer.files]));

  function stopCamera() { cameraGeneration++; if (stream) stream.getTracks().forEach(track => track.stop()); stream = null; $('cameraVideo').srcObject = null; updateControls(); }
  function closeCamera() { stopCamera(); $('cameraDialog').close(); $('takePhoto').focus(); }
  async function startCamera() {
    stopCamera(); const generation = cameraGeneration;
    $('cameraStatus').textContent = 'Opening camera…'; $('switchCamera').disabled = true;
    if (!navigator.mediaDevices?.getUserMedia) { $('cameraStatus').textContent = 'Live preview requires HTTPS and a supported browser. Try “Use device camera” or choose a photo from your gallery.'; return; }
    try {
      const incoming = await navigator.mediaDevices.getUserMedia({video: {facingMode: {ideal: facing}, width: {ideal: 1600}, height: {ideal: 1200}}, audio: false});
      if (generation !== cameraGeneration || !$('cameraDialog').open) { incoming.getTracks().forEach(track => track.stop()); return; }
      stream = incoming; $('cameraVideo').srcObject = stream; await $('cameraVideo').play();
      $('cameraStatus').textContent = 'Keep the affected plant in focus, then capture.';
      $('switchCamera').disabled = false; updateControls();
    } catch (error) {
      if (generation !== cameraGeneration) return;
      stopCamera();
      $('cameraStatus').textContent = error.name === 'NotAllowedError' ? 'Camera permission was denied. Allow it in browser settings or choose photos from your gallery.' : 'No available camera could be opened. Use device camera or choose a photo from your gallery.';
    }
  }
  $('takePhoto').addEventListener('click', () => { $('cameraDialog').showModal(); startCamera(); });
  $('closeCamera').addEventListener('click', closeCamera);
  $('cameraDialog').addEventListener('cancel', event => { event.preventDefault(); closeCamera(); });
  $('cameraDialog').addEventListener('close', stopCamera);
  $('nativeCamera').addEventListener('click', () => { closeCamera(); $('nativeCameraInput').click(); });
  $('switchCamera').addEventListener('click', () => { facing = facing === 'environment' ? 'user' : 'environment'; startCamera(); });
  $('capturePhoto').addEventListener('click', async () => {
    const video = $('cameraVideo');
    if (!stream || !video.videoWidth || preparing || photos.length >= 5) return;
    $('capturePhoto').disabled = true;
    const canvas = document.createElement('canvas'); canvas.width = video.videoWidth; canvas.height = video.videoHeight;
    canvas.getContext('2d').drawImage(video, 0, 0);
    const blob = await new Promise(resolve => canvas.toBlob(resolve, 'image/jpeg', 0.9));
    if (blob) await addPhotos([new File([blob], `camera-${Date.now()}.jpg`, {type: 'image/jpeg'})]);
    updateControls();
    if ($('cameraDialog').open) $('cameraStatus').textContent = `${photos.length} of 5 photos added. Capture another angle or close the camera.`;
  });
  document.addEventListener('visibilitychange', () => { if (document.hidden && $('cameraDialog').open) closeCamera(); });
  window.addEventListener('pagehide', stopCamera);

  function goToStep(nextStep) {
    step = nextStep;
    panes.forEach((pane, index) => { pane.style.display = index + 1 === step ? 'block' : 'none'; });
    for (let index = 1; index <= 4; index++) { const marker = $(`step-ind-${index}`); marker.classList.toggle('active', index === step); marker.classList.toggle('completed', index < step); marker.setAttribute('aria-current', index === step ? 'step' : 'false'); }
    $('btn-prev').style.display = step === 2 || step === 3 ? 'inline-block' : 'none';
    $('btn-next').style.display = step === 2 ? 'inline-block' : 'none';
    $('btn-submit').style.display = step === 3 ? 'inline-block' : 'none';
    $('uploadConsent').hidden = step !== 3;
    const heading = panes[step - 1].querySelector('h4, h3');
    if (heading) { heading.tabIndex = -1; heading.focus({preventScroll: true}); }
    if (!reducedMotion) panes[step - 1].animate([{opacity: 0, transform: 'translateY(5px)'}, {opacity: 1, transform: 'translateY(0)'}], {duration: 160, easing: 'ease-out'});
  }
  function validate() {
    if (!$('selected_crop_id').value) { goToStep(1); showError('Select a crop to continue.'); return false; }
    if (step >= 2 && !photos.length) { goToStep(2); showError('Add at least one clear plant photo.'); return false; }
    return true;
  }
  $('btn-next').addEventListener('click', () => { showError(''); if (!preparing && validate()) goToStep(step + 1); });
  $('btn-prev').addEventListener('click', () => { showError(''); goToStep(step - 1); });
  document.querySelectorAll('[name="treatment_applied"]').forEach(input => input.addEventListener('change', () => { $('treatmentDetailsGroup').hidden = input.value !== 'Yes'; }));
  function flattenErrors(value) {
    if (typeof value === 'string') return value;
    if (Array.isArray(value)) return value.map(flattenErrors).join(' ');
    if (value && typeof value === 'object') return Object.entries(value).map(([key, item]) => `${key}: ${flattenErrors(item)}`).join(' ');
    return '';
  }
  form.addEventListener('submit', event => {
    event.preventDefault();
    if (submitting || preparing || !validate()) return;
    if (step !== 3) { goToStep(Math.min(step + 1, 3)); return; }
    submitting = true; showError(''); updateControls(); goToStep(4);
    const data = new FormData(form); photos.forEach(photo => data.append('images', photo.file));
    const xhr = new XMLHttpRequest(); xhr.open('POST', form.dataset.apiUrl); xhr.timeout = Number(form.dataset.requestTimeout) || 150000;
    xhr.setRequestHeader('X-CSRFToken', data.get('csrfmiddlewaretoken')); xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
    $('loadingStatusText').textContent = `Uploading ${photos.length} photo${photos.length === 1 ? '' : 's'}…`;
    $('loadingSubText').textContent = 'Your assessment starts as soon as the upload completes.';
    $('uploadProgress').style.width = '0%';
    xhr.upload.onprogress = event => { if (event.lengthComputable) { const pct = Math.round(event.loaded / event.total * 100); $('uploadProgress').style.width = `${pct}%`; $('uploadProgress').setAttribute('aria-valuenow', String(pct)); } };
    xhr.upload.onload = () => { $('loadingStatusText').textContent = 'Preparing your assessment…'; $('loadingSubText').textContent = 'Checking your photos and reported symptoms. This may take a moment.'; };
    const fail = message => { submitting = false; updateControls(); goToStep(3); showError(message); };
    xhr.onload = () => {
      let result; try { result = JSON.parse(xhr.responseText); } catch (_) { result = {}; }
      if (xhr.status === 201 && result.result_url) { location.assign(result.result_url); return; }
      fail(flattenErrors(result.errors || result.error || result.detail || result) || (xhr.status === 403 ? 'Your session expired. Refresh the page before trying again.' : 'Assessment failed. Your photos are still selected; please retry.'));
    };
    xhr.onerror = () => fail('Connection lost. Your photos are still selected. Check your connection and retry.');
    xhr.ontimeout = () => fail('The assessment took too long. Check your dashboard before retrying. Your photos are still selected.');
    xhr.send(data);
  });
  window.addEventListener('pagehide', event => { if (!event.persisted) photos.forEach(photo => URL.revokeObjectURL(photo.url)); });
  goToStep(preselected ? 2 : 1); renderPhotos();
});
