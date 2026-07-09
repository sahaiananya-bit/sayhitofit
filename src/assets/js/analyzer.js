// SAYHITOFIT — Body Analyzer page
document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('analyzer-form');
  if (!form) return;

  const emptyState = document.getElementById('results-empty');
  const loadingState = document.getElementById('loading-state');
  const errorBox = document.getElementById('error-box');
  const results = document.getElementById('results');
  const analyzeBtn = document.getElementById('analyze-btn');

  let macroChart = null;
  let photoDataUrl = null;

  // ---------- Physique photo picker ----------
  const photoInput = document.getElementById('an-photo');
  const photoPick = document.getElementById('photo-pick');
  const photoDrop = document.getElementById('photo-drop');
  const photoPreview = document.getElementById('photo-preview');
  const photoThumb = document.getElementById('photo-thumb');
  const photoRemove = document.getElementById('photo-remove');

  photoPick.addEventListener('click', () => photoInput.click());

  photoInput.addEventListener('change', () => {
    const file = photoInput.files && photoInput.files[0];
    if (!file) return;
    // Downscale in the browser so we never ship a huge upload.
    const img = new Image();
    img.onload = () => {
      const MAX = 768;
      const scale = Math.min(1, MAX / Math.max(img.width, img.height));
      const canvas = document.createElement('canvas');
      canvas.width = Math.round(img.width * scale);
      canvas.height = Math.round(img.height * scale);
      canvas.getContext('2d').drawImage(img, 0, 0, canvas.width, canvas.height);
      photoDataUrl = canvas.toDataURL('image/jpeg', 0.85);
      URL.revokeObjectURL(img.src);
      photoThumb.src = photoDataUrl;
      photoDrop.style.display = 'none';
      photoPreview.style.display = 'flex';
    };
    img.onerror = () => { alert('That file could not be read as an image.'); };
    img.src = URL.createObjectURL(file);
  });

  photoRemove.addEventListener('click', () => {
    photoDataUrl = null;
    photoInput.value = '';
    photoThumb.src = '';
    photoPreview.style.display = 'none';
    photoDrop.style.display = 'flex';
  });

  const show = (el) => { el.style.display = ''; };
  const hide = (el) => { el.style.display = 'none'; };

  function setState(state) {
    [emptyState, loadingState, errorBox, results].forEach(hide);
    if (state === 'empty') show(emptyState);
    if (state === 'loading') show(loadingState);
    if (state === 'error') show(errorBox);
    if (state === 'results') show(results);
  }

  form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const num = (id) => {
      const v = parseFloat(document.getElementById(id).value);
      return Number.isFinite(v) ? v : null;
    };

    const payload = {
      height_cm: num('an-height'),
      weight_kg: num('an-weight'),
      age: num('an-age'),
      gender: document.getElementById('an-gender').value,
      activity_level: document.getElementById('an-activity').value,
      fitness_goal: document.getElementById('an-goal').value
    };

    if (!payload.height_cm || !payload.weight_kg || !payload.age) {
      errorBox.textContent = 'Height, weight and age are required.';
      setState('error');
      return;
    }

    const waist = num('an-waist');
    const hip = num('an-hip');
    const neck = num('an-neck');
    if (waist) payload.waist_cm = waist;
    if (hip) payload.hip_cm = hip;
    if (neck) payload.neck_cm = neck;
    if (photoDataUrl) payload.photo_data_url = photoDataUrl;

    setState('loading');
    analyzeBtn.disabled = true;

    try {
      const response = await fetch('/api/analyze-body-composition', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const body = await response.json();
      if (!response.ok) {
        throw new Error(typeof body.detail === 'string' ? body.detail : 'The analysis failed. Check your inputs.');
      }
      renderResults(body.data);
      setState('results');
      results.scrollIntoView({ behavior: 'smooth', block: 'start' });
    } catch (err) {
      errorBox.textContent = err.message === 'Failed to fetch'
        ? 'Could not reach the server. Open the site via the FastAPI app (http://localhost:8000).'
        : err.message;
      setState('error');
    } finally {
      analyzeBtn.disabled = false;
    }
  });

  function metricCell(k, v, unit) {
    return `<div class="metric"><span class="k">${k}</span><span class="v">${v}${unit ? ` <small>${unit}</small>` : ''}</span></div>`;
  }

  function renderResults(d) {
    // Plan source badge
    const source = document.getElementById('plan-source');
    if (d.plan_source === 'ai') {
      source.textContent = 'Plan written by AI model';
      source.classList.add('ai');
    } else {
      source.textContent = 'Plan from coaching rules';
      source.classList.remove('ai');
    }

    // Headline metrics
    document.getElementById('metric-grid').innerHTML = [
      metricCell('BMI', d.bmi, d.bmi_category),
      d.body_fat_percentage != null ? metricCell('Body fat', d.body_fat_percentage, '%') : '',
      metricCell('Lean mass', d.lean_mass_kg, 'kg'),
      metricCell('BMR', Math.round(d.bmr), 'kcal'),
      metricCell('TDEE', Math.round(d.tdee), 'kcal')
    ].join('');

    // Photo assessment (only present when a photo was uploaded)
    const photoBlock = document.getElementById('photo-block');
    const photoBody = document.getElementById('photo-analysis-body');
    if (d.photo_analysis) {
      if (d.photo_analysis.unavailable) {
        photoBody.innerHTML = `<p class="photo-note-muted">${d.photo_analysis.reason}</p>`;
      } else {
        const p = d.photo_analysis;
        photoBody.innerHTML = `
          <div class="photo-range">${p.estimated_body_fat_range}</div>
          <div class="photo-confidence">estimated from photo · ${p.confidence} confidence</div>
          <ul>${p.observations.map(o => `<li>${o}</li>`).join('')}</ul>
          <p class="photo-note-muted" style="margin-top:0.75rem;">A photo supports a rough range only — tape measurements give the number used in your metrics above.</p>`;
      }
      photoBlock.style.display = '';
    } else {
      photoBlock.style.display = 'none';
    }

    // Calories
    const cal = d.caloric_recommendation;
    document.getElementById('calorie-grid').innerHTML = [
      metricCell('Maintain', Math.round(cal.maintenance), 'kcal'),
      metricCell('To lose', Math.round(cal.deficit_loss), 'kcal'),
      metricCell('To gain', Math.round(cal.surplus_gain), 'kcal')
    ].join('');

    // Macro chart
    const m = d.macro_breakdown;
    const ctx = document.getElementById('macro-chart');
    if (macroChart) macroChart.destroy();
    macroChart = new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels: ['Protein', 'Carbs', 'Fats'],
        datasets: [{
          data: [m.protein.grams, m.carbs.grams, m.fats.grams],
          backgroundColor: ['#ff6b35', '#0a0a0a', '#e5e5e5'],
          borderColor: '#ffffff',
          borderWidth: 3
        }]
      },
      options: {
        plugins: { legend: { display: false } },
        cutout: '65%'
      }
    });
    document.getElementById('macro-legend').innerHTML =
      `<span><i class="swatch" style="background:#ff6b35"></i>Protein ${m.protein.grams} g</span>` +
      `<span><i class="swatch" style="background:#0a0a0a"></i>Carbs ${m.carbs.grams} g</span>` +
      `<span><i class="swatch" style="background:#e5e5e5"></i>Fats ${m.fats.grams} g</span>`;

    // Timeline
    const timelineBlock = document.getElementById('timeline-block');
    if (d.timeline && d.timeline.weeks_to_goal) {
      const dir = d.weight_suggestion === 'decrease' ? 'losing' : 'gaining';
      document.getElementById('timeline-text').textContent =
        `At a steady ${d.timeline.weekly_change_kg} kg per week, you reach the healthy-range target in about ` +
        `${d.timeline.weeks_to_goal} weeks (${d.timeline.target_date}) — assuming consistent training and ${dir} at the recommended rate.`;
      show(timelineBlock);
    } else {
      hide(timelineBlock);
    }

    // Workout plan
    document.getElementById('workout-title').textContent = d.workout_plan.split_name;
    document.getElementById('workout-days').innerHTML = d.workout_plan.weekly_schedule.map(day => `
      <div class="plan-day">
        <div class="plan-day-head"><span>${day.day}</span><span class="focus">${day.focus}</span></div>
        <table>
          <thead><tr><th>Exercise</th><th>Sets</th><th>Reps</th><th>Rest</th></tr></thead>
          <tbody>
            ${day.exercises.map(ex =>
              `<tr><td>${ex.name}</td><td>${ex.sets}</td><td>${ex.reps}</td><td>${ex.rest}</td></tr>`
            ).join('')}
          </tbody>
        </table>
      </div>`).join('');

    // Nutrition plan
    document.getElementById('nutrition-title').textContent = d.nutrition_plan.template_name;
    document.getElementById('meal-rows').innerHTML = d.nutrition_plan.daily_meals.map(meal => `
      <div class="meal-row">
        <div class="meal-name">${meal.meal}</div>
        <ul>${meal.suggestions.map(s => `<li>${s}</li>`).join('')}</ul>
      </div>`).join('');
    document.getElementById('pantry-tags').innerHTML =
      d.nutrition_plan.pantry_staples.map(p => `<span>${p}</span>`).join('');

    // Advice
    document.getElementById('advice-text').textContent = (d.personalized_advice || '').replaceAll('✓ ', '');
  }
});
