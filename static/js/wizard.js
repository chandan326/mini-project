/**
 * AgriHealth AI - 5-Step Diagnosis Wizard Client Logic
 */

document.addEventListener('DOMContentLoaded', function () {
  const wizardForm = document.getElementById('diagnosisWizardForm');
  if (!wizardForm) return;

  let currentStep = 1;
  const totalSteps = 4; // Steps 1 to 4 in form, Step 5 is Result page

  const stepElements = {
    1: document.getElementById('step-1-crop'),
    2: document.getElementById('step-2-photos'),
    3: document.getElementById('step-3-questions'),
    4: document.getElementById('step-4-loading')
  };

  const btnNext = document.getElementById('btn-next');
  const btnPrev = document.getElementById('btn-prev');
  const btnSubmit = document.getElementById('btn-submit');
  const hiddenCropInput = document.getElementById('selected_crop_id');

  // --- Step 1: Crop Selection ---
  const cropCards = document.querySelectorAll('.crop-select-card');
  cropCards.forEach(card => {
    card.addEventListener('click', function () {
      cropCards.forEach(c => c.classList.remove('selected'));
      this.classList.add('selected');
      const cropId = this.getAttribute('data-crop-id');
      hiddenCropInput.value = cropId;
      if (btnNext) btnNext.disabled = false;
    });
  });

  // Search Crop Filter
  const cropSearchInput = document.getElementById('cropSearchInput');
  if (cropSearchInput) {
    cropSearchInput.addEventListener('input', function () {
      const query = this.value.toLowerCase().trim();
      cropCards.forEach(card => {
        const name = card.getAttribute('data-crop-name').toLowerCase();
        if (name.includes(query)) {
          card.style.display = 'block';
        } else {
          card.style.display = 'none';
        }
      });
    });
  }

  // --- Step 2: 5 Image Upload Slots & Previews ---
  for (let i = 1; i <= 5; i++) {
    const fileInput = document.getElementById(`image_${i}`);
    const slotCard = document.getElementById(`slot-card-${i}`);
    const previewContainer = document.getElementById(`slot-preview-${i}`);

    if (fileInput && slotCard) {
      fileInput.addEventListener('change', function (e) {
        const file = e.target.files[0];
        if (file) {
          // Check client-side lighting & contrast hints
          const reader = new FileReader();
          reader.onload = function (evt) {
            previewContainer.innerHTML = `
              <div class="position-relative">
                <img src="${evt.target.result}" class="upload-preview-img mb-2" alt="Photo ${i}">
                <button type="button" class="btn btn-sm btn-danger position-absolute top-0 end-0 rounded-circle py-0 px-2" onclick="clearSlot(${i})">&times;</button>
              </div>
              <small class="text-success fw-bold d-block"><i class="fas fa-check-circle"></i> Photo ${i} Loaded</small>
            `;
            slotCard.classList.add('border-success');
          };
          reader.readAsDataURL(file);
        }
      });
    }
  }

  window.clearSlot = function (slotIndex) {
    const fileInput = document.getElementById(`image_${slotIndex}`);
    const slotCard = document.getElementById(`slot-card-${slotIndex}`);
    const previewContainer = document.getElementById(`slot-preview-${slotIndex}`);
    if (fileInput) fileInput.value = '';
    if (slotCard) slotCard.classList.remove('border-success');
    if (previewContainer) {
      previewContainer.innerHTML = `
        <i class="fas fa-camera fa-2x text-success mb-2"></i>
        <span class="fw-bold d-block">Photo ${slotIndex}</span>
        <small class="text-muted">Tap to upload / capture</small>
      `;
    }
  };

  // --- Step Navigation Buttons ---
  if (btnNext) {
    btnNext.addEventListener('click', function () {
      if (validateStep(currentStep)) {
        goToStep(currentStep + 1);
      }
    });
  }

  if (btnPrev) {
    btnPrev.addEventListener('click', function () {
      if (currentStep > 1) {
        goToStep(currentStep - 1);
      }
    });
  }

  function validateStep(step) {
    if (step === 1) {
      if (!hiddenCropInput.value) {
        alert('Please select a crop to proceed.');
        return false;
      }
    }
    if (step === 2) {
      // Check if at least 1 image uploaded
      let uploadedCount = 0;
      for (let i = 1; i <= 5; i++) {
        const inp = document.getElementById(`image_${i}`);
        if (inp && inp.files.length > 0) uploadedCount++;
      }
      if (uploadedCount < 1) {
        alert('Please upload at least 1 clear image of the affected plant.');
        return false;
      }
    }
    return true;
  }

  function goToStep(step) {
    // Hide all steps
    Object.keys(stepElements).forEach(s => {
      if (stepElements[s]) stepElements[s].style.display = 'none';
    });

    // Update Step Indicators
    for (let i = 1; i <= totalSteps; i++) {
      const ind = document.getElementById(`step-ind-${i}`);
      if (ind) {
        ind.classList.remove('active', 'completed');
        if (i < step) ind.classList.add('completed');
        if (i === step) ind.classList.add('active');
      }
    }

    currentStep = step;
    if (stepElements[step]) stepElements[step].style.display = 'block';

    // Button states
    if (btnPrev) btnPrev.style.display = (step === 1 || step === 4) ? 'none' : 'inline-block';
    if (btnNext) btnNext.style.display = (step === 3 || step === 4) ? 'none' : 'inline-block';
    if (btnSubmit) btnSubmit.style.display = (step === 3) ? 'inline-block' : 'none';

    // Step 4 Loading Trigger
    if (step === 4) {
      runLoadingSequence();
      setTimeout(() => {
        wizardForm.submit();
      }, 2500);
    }
  }

  function runLoadingSequence() {
    const loadingStatusText = document.getElementById('loadingStatusText');
    const loadingSubText = document.getElementById('loadingSubText');
    const stages = [
      { main: "Analyzing plant photos...", sub: "Validating resolution, contrast, and image patterns" },
      { main: "Evaluating reported symptoms...", sub: "Correlating farmer questionnaire inputs" },
      { main: "Running AI ensemble prediction model...", sub: "Calculating disease probability distribution" },
      { main: "Verifying with Agricultural Knowledge Base...", sub: "Fetching verified care & treatment guidelines" }
    ];

    let idx = 0;
    const interval = setInterval(() => {
      idx++;
      if (idx < stages.length) {
        if (loadingStatusText) loadingStatusText.innerText = stages[idx].main;
        if (loadingSubText) loadingSubText.innerText = stages[idx].sub;
      } else {
        clearInterval(interval);
      }
    }, 600);
  }

  if (wizardForm) {
    wizardForm.addEventListener('submit', function (e) {
      if (currentStep === 3) {
        e.preventDefault();
        goToStep(4);
      }
    });
  }
});
