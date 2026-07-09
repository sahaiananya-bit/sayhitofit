// SAYHITOFIT — site behavior (nav, hero bento scroll, method rotation, BMI, contact)
document.addEventListener('DOMContentLoaded', () => {
  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // ---------- Mobile navigation ----------
  const menuToggle = document.querySelector('.menu-toggle');
  const navList = document.getElementById('nav-list');

  if (menuToggle && navList) {
    menuToggle.addEventListener('click', () => {
      const open = navList.classList.toggle('open');
      menuToggle.setAttribute('aria-expanded', String(open));
    });
    navList.querySelectorAll('a').forEach(link => {
      link.addEventListener('click', () => {
        navList.classList.remove('open');
        menuToggle.setAttribute('aria-expanded', 'false');
      });
    });
  }

  // ---------- Floating pill header ----------
  const header = document.querySelector('header');
  const onHeaderScroll = () => header.classList.toggle('scrolled', window.scrollY > 50);
  window.addEventListener('scroll', onHeaderScroll, { passive: true });
  onHeaderScroll();

  // ---------- Hero: giant word letters ----------
  const heroWordText = document.getElementById('hero-word-text');
  if (heroWordText) {
    const word = 'SAYHITOFIT';
    heroWordText.innerHTML = word
      .split('')
      .map((ch, i) => `<span style="animation-delay:${i * 0.08}s">${ch}</span>`)
      .join('');
  }

  // ---------- Hero: scroll-scrubbed bento (ported from the MONO reference) ----------
  const heroTrack = document.getElementById('hero-track');
  const heroWord = document.getElementById('hero-word');
  const heroCenter = document.getElementById('hero-center');
  const heroColLeft = document.getElementById('hero-col-left');
  const heroColRight = document.getElementById('hero-col-right');
  const heroTagline = document.getElementById('hero-tagline');
  const heroBento = document.querySelector('.hero-bento');
  const heroMedia = heroCenter ? heroCenter.querySelector('video, img.hero-center-media') : null;

  if (heroTrack && !reducedMotion) {
    let rafId = null;

    const updateHero = () => {
      const rect = heroTrack.getBoundingClientRect();
      // Real scrub distance: track height minus the sticky viewport.
      const scrollableHeight = heroTrack.offsetHeight - window.innerHeight;
      const scrolled = -rect.top;
      const progress = Math.max(0, Math.min(1, scrolled / scrollableHeight));

      // Word fades 0-0.15, images fully assemble by 0.6, then HOLD
      // assembled for the rest of the scrub so the grid stays visible.
      const textOpacity = Math.max(0, 1 - progress / 0.15);
      const imageProgress = Math.max(0, Math.min(1, (progress - 0.15) / 0.45));

      const centerWidth = 100 - imageProgress * 80;   // 100% -> 20%
      const sideWidth = imageProgress * 40;             // 0% -> 40% (2 cols)
      const sideOpacity = imageProgress;
      const translateLeft = -100 + imageProgress * 100; // -100% -> 0%
      const translateRight = 100 - imageProgress * 100; // 100% -> 0%
      const gap = imageProgress * 8;

      heroWord.style.opacity = textOpacity;
      heroTagline.style.opacity = textOpacity;
      heroBento.style.gap = `${gap}px`;
      // The word sits behind the video; fade the video in as the word fades out
      // so the two never fight for the same pixels.
      if (heroMedia) heroMedia.style.opacity = Math.max(0.15, 1 - textOpacity);

      heroCenter.style.width = `${centerWidth}%`;

      heroColLeft.style.width = `${sideWidth}%`;
      heroColLeft.style.gap = `${gap}px`;
      heroColLeft.style.opacity = sideOpacity;
      heroColLeft.style.transform = `translateX(${translateLeft}%)`;

      heroColRight.style.width = `${sideWidth}%`;
      heroColRight.style.gap = `${gap}px`;
      heroColRight.style.opacity = sideOpacity;
      heroColRight.style.transform = `translateX(${translateRight}%)`;
    };

    const onScroll = () => {
      if (rafId) cancelAnimationFrame(rafId);
      rafId = requestAnimationFrame(updateHero);
    };

    window.addEventListener('scroll', onScroll, { passive: true });
    updateHero();
  } else if (heroCenter) {
    // Reduced motion: show the full bento immediately, skip the scrub.
    heroCenter.style.width = '20%';
    heroColLeft.style.width = '40%';
    heroColRight.style.width = '40%';
    heroColLeft.style.opacity = 1;
    heroColRight.style.opacity = 1;
    heroWord.style.opacity = 0;
    heroTagline.style.opacity = 1;
    if (heroMedia) heroMedia.style.opacity = 1;
  }

  // ---------- Method section: 3D rotating headline + blur-word paragraph ----------
  const methodTrack = document.getElementById('method-track');
  const headlines = document.querySelectorAll('.method-headline');
  const methodParagraph = document.getElementById('method-paragraph');

  if (methodTrack && headlines.length) {
    if (methodParagraph && !methodParagraph.dataset.wrapped) {
      const words = methodParagraph.textContent.trim().split(/\s+/);
      methodParagraph.innerHTML = words.map(w => `<span>${w}</span>`).join(' ');
      methodParagraph.dataset.wrapped = 'true';
    }
    const wordSpans = methodParagraph ? methodParagraph.querySelectorAll('span') : [];

    let rafId = null;

    const updateMethod = () => {
      const rect = methodTrack.getBoundingClientRect();
      const scrollableRange = methodTrack.offsetHeight - window.innerHeight;
      const scrolled = -rect.top;
      const progress = Math.max(0, Math.min(1, scrolled / Math.max(1, scrollableRange)));

      if (!reducedMotion) {
        const segment = 1 / headlines.length;
        headlines.forEach((h, index) => {
          const start = index * segment;
          const end = (index + 1) * segment;
          const isLast = index === headlines.length - 1;
          let rotateX = 90;
          let opacity = 0;

          if (progress >= start && progress < end) {
            const local = (progress - start) / segment;
            rotateX = (1 - local) * 90;
            opacity = local;
          } else if (progress >= end) {
            if (isLast) { rotateX = 0; opacity = 1; }
            else { rotateX = -90; opacity = 0; }
          }

          h.style.transform = `rotateX(${rotateX}deg)`;
          h.style.opacity = opacity;
        });
      } else {
        headlines.forEach((h, i) => {
          h.style.opacity = i === headlines.length - 1 ? 1 : 0;
          h.style.transform = 'none';
        });
      }

      if (wordSpans.length) {
        const descRect = methodParagraph.getBoundingClientRect();
        const startTrigger = window.innerHeight * 0.8;
        const endTrigger = window.innerHeight * 0.2;
        let descProgress = 0;
        if (descRect.top < startTrigger) {
          descProgress = Math.max(0, Math.min(1, (startTrigger - descRect.top) / (startTrigger - endTrigger)));
        }
        wordSpans.forEach((span, i) => {
          const wp = Math.max(0, Math.min(1, descProgress * wordSpans.length - i));
          span.style.opacity = reducedMotion ? 1 : wp;
          span.style.filter = reducedMotion ? 'none' : `blur(${(1 - wp) * 12}px)`;
        });
      }
    };

    const onMethodScroll = () => {
      if (rafId) cancelAnimationFrame(rafId);
      rafId = requestAnimationFrame(updateMethod);
    };

    window.addEventListener('scroll', onMethodScroll, { passive: true });
    updateMethod();
  }

  // ---------- Scroll-reveal for plain sections ----------
  const revealTargets = document.querySelectorAll('.wrap, .bento-grid, .quote-media');
  if ('IntersectionObserver' in window && !reducedMotion) {
    const io = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('reveal-up', 'in-view');
          io.unobserve(entry.target);
        }
      });
    }, { threshold: 0.15 });
    revealTargets.forEach(t => io.observe(t));
  }

  // ---------- BMI calculator ----------
  const calculateBmiBtn = document.getElementById('calculate-bmi');
  if (calculateBmiBtn) {
    const resetBmiBtn = document.getElementById('reset-bmi');
    const bmiResult = document.getElementById('bmi-result');
    const bmiPlaceholder = document.getElementById('bmi-placeholder');
    const bmiValue = document.getElementById('bmi-value');
    const bmiCategory = document.getElementById('bmi-category');
    const bmiInfo = document.getElementById('bmi-info');

    const unitBtns = document.querySelectorAll('.unit-btn');
    const metricInputs = document.getElementById('metric-inputs');
    const imperialInputs = document.getElementById('imperial-inputs');

    const heightCm = document.getElementById('height-cm');
    const weightKg = document.getElementById('weight-kg');
    const heightFeet = document.getElementById('height-feet');
    const heightInches = document.getElementById('height-inches');
    const weightLbs = document.getElementById('weight-lbs');

    let currentUnit = 'metric';

    unitBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        unitBtns.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        currentUnit = btn.getAttribute('data-unit');
        metricInputs.style.display = currentUnit === 'metric' ? 'block' : 'none';
        imperialInputs.style.display = currentUnit === 'metric' ? 'none' : 'block';
        hideResult();
      });
    });

    function hideResult() {
      bmiResult.style.display = 'none';
      bmiPlaceholder.style.display = 'block';
    }

    function calculateBMI() {
      let bmi;
      if (currentUnit === 'metric') {
        const height = parseFloat(heightCm.value);
        const weight = parseFloat(weightKg.value);
        if (!height || !weight || height <= 0 || weight <= 0) {
          alert('Please enter valid height and weight values');
          return;
        }
        bmi = weight / ((height / 100) ** 2);
      } else {
        const feet = parseFloat(heightFeet.value);
        const inches = parseFloat(heightInches.value) || 0;
        const weight = parseFloat(weightLbs.value);
        if (!feet || feet < 0 || inches < 0 || !weight || weight <= 0) {
          alert('Please enter valid height and weight values');
          return;
        }
        const totalInches = feet * 12 + inches;
        bmi = (weight * 703) / (totalInches * totalInches);
      }
      displayBMIResult(bmi);
    }

    function displayBMIResult(bmi) {
      bmiValue.textContent = bmi.toFixed(1);

      let category, info;
      if (bmi < 18.5) {
        category = 'Underweight';
        info = 'You are under the healthy range. A coach can help you build up safely — strength work plus a calorie surplus.';
      } else if (bmi < 25) {
        category = 'Normal weight';
        info = 'You are in the healthy range. Focus on maintaining it with consistent training and good food.';
      } else if (bmi < 30) {
        category = 'Overweight';
        info = 'You are above the healthy range. Structured training and a moderate deficit will move this steadily.';
      } else {
        category = 'Obese';
        info = 'Start with low-impact work — walking, swimming, fundamentals. Our beginner program is built for exactly this.';
      }

      bmiCategory.textContent = category;
      bmiInfo.textContent = info;
      bmiPlaceholder.style.display = 'none';
      bmiResult.style.display = 'block';
    }

    function resetBMI() {
      [heightCm, weightKg, heightFeet, heightInches, weightLbs].forEach(el => { el.value = ''; });
      hideResult();
    }

    calculateBmiBtn.addEventListener('click', calculateBMI);
    resetBmiBtn.addEventListener('click', resetBMI);

    [heightCm, weightKg, heightInches, weightLbs].forEach(el => {
      el.addEventListener('keypress', e => { if (e.key === 'Enter') calculateBMI(); });
    });
    heightFeet.addEventListener('keypress', e => { if (e.key === 'Enter') heightInches.focus(); });
  }

  // ---------- Contact form ----------
  const contactForm = document.getElementById('contact-form');
  if (contactForm) {
    const contactResponse = document.getElementById('contact-response');
    const responseText = document.getElementById('response-text');

    contactForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      contactResponse.classList.remove('error');

      try {
        const response = await fetch('/api/contact', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            name: document.getElementById('contact-name').value,
            email: document.getElementById('contact-email').value,
            message: document.getElementById('contact-message').value
          })
        });
        const data = await response.json();

        if (response.ok) {
          responseText.textContent = data.message;
          contactResponse.style.display = 'block';
          contactForm.reset();
          setTimeout(() => { contactResponse.style.display = 'none'; }, 6000);
        } else {
          responseText.textContent = 'Error: ' + (data.detail || 'Failed to send message');
          contactResponse.classList.add('error');
          contactResponse.style.display = 'block';
        }
      } catch (err) {
        responseText.textContent = 'Could not reach the server. Is the site running through the FastAPI app?';
        contactResponse.classList.add('error');
        contactResponse.style.display = 'block';
        console.error(err);
      }
    });
  }
});
