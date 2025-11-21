document.addEventListener('DOMContentLoaded', () => {
  const ageEl = document.getElementById('age');
  const genderEl = document.getElementById('gender');
  const inputAge = document.getElementById('inputAge');
  const inputGender = document.getElementById('inputGender');
  const inputPrefs = document.getElementById('inputPrefs');
  const saveProfile = document.getElementById('saveProfile');
  const submitFeedback = document.getElementById('submitFeedback');
  const comment = document.getElementById('comment');
  const rating = document.getElementById('rating');
  const engageResult = document.getElementById('engageResult');
  const getJoke = document.getElementById('getJoke');
  const getPic = document.getElementById('getPic');

  function loadProfile() {
    const stored = localStorage.getItem('patient_profile');
    if (stored) {
      const p = JSON.parse(stored);
      ageEl.textContent = p.age;
      genderEl.textContent = p.gender;
      inputAge.value = p.age;
      inputGender.value = p.gender;
      inputPrefs.value = p.prefs || '';
      document.getElementById('patientName').textContent = `Hi ${p.name || 'Friend'}!`;
    } else {
      ageEl.textContent = inputAge.value;
      genderEl.textContent = inputGender.value;
    }
  }

  function saveProfileLocally() {
    const profile = {
      name: 'Friend',
      age: parseInt(inputAge.value, 10) || 8,
      gender: inputGender.value || 'nonbinary',
      prefs: inputPrefs.value || ''
    };
    localStorage.setItem('patient_profile', JSON.stringify(profile));
    loadProfile();
  }

  saveProfile.addEventListener('click', saveProfileLocally);

  submitFeedback.addEventListener('click', async () => {
    const profile = JSON.parse(localStorage.getItem('patient_profile') || '{}');
    const payload = {
      patient_id: typeof PATIENT_ID !== 'undefined' ? PATIENT_ID : 'public_demo',
      interaction_type: 'patient_ui',
      action: 'feedback_submission',
      feedback_type: 'direct',
      rating: parseInt(rating.value, 10) || 4,
      comment: comment.value || '',
      meta: { profile }
    };

    try {
      const res = await fetch('/public/feedback/submit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      if (res.ok) {
        engageResult.textContent = 'Thanks! Your feedback was sent.';
        comment.value = '';
      } else {
        engageResult.textContent = 'Oops — could not send feedback.';
      }
    } catch (e) {
      engageResult.textContent = 'Network error — try again later.';
    }
  });

  getJoke.addEventListener('click', async () => {
    engageResult.textContent = 'Thinking of a funny one...';
    try {
      const res = await fetch(`/public/assistant/engage/${typeof PATIENT_ID !== 'undefined' ? PATIENT_ID : 'public_demo'}`);
      const data = await res.json();
      engageResult.innerHTML = `<div class="joke">${data.joke || data.text || 'Here is a silly thought!'}</div>`;
    } catch (e) {
      engageResult.textContent = 'Could not fetch a joke right now.';
    }
  });

  getPic.addEventListener('click', async () => {
    engageResult.textContent = 'Finding a cheerful picture...';
    try {
      const res = await fetch(`/public/assistant/engage/${typeof PATIENT_ID !== 'undefined' ? PATIENT_ID : 'public_demo'}?mode=pic`);
      const data = await res.json();
      if (data.image_url) {
        engageResult.innerHTML = `<img src="${data.image_url}" alt="cheerful image" class="cheer-img"/>`;
      } else {
        engageResult.textContent = data.text || 'No image found.';
      }
    } catch (e) {
      engageResult.textContent = 'Could not fetch image right now.';
    }
  });

  // initialize
  loadProfile();
});
