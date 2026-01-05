// assets/js/main.js
document.addEventListener("DOMContentLoaded", () => {
  // Initialize GSAP
  gsap.registerPlugin(ScrollTrigger, ScrollToPlugin);

  // Hero video and content
  const heroVideo = document.querySelector('.hero-video');
  const heroContent = document.querySelector('.hero-content');

  // Function to handle video loaded
  heroVideo.addEventListener('loadeddata', () => {
      // Once video is loaded, animate in the hero content
      gsap.to(heroContent, {
          opacity: 1,
          visibility: 'visible',
          duration: 1,
          delay: 0.5, // Half second delay after video loads
          ease: 'power2.out'
      });

      // Animate the title lines sequentially
      gsap.from('.hero-title .line', {
          y: 100,
          opacity: 0,
          duration: 0.8,
          stagger: 0.2,
          ease: 'power3.out'
      });

      // Animate the button
      gsap.from('.join-now-btn', {
          scale: 0.8,
          opacity: 0,
          duration: 0.5,
          delay: 1.2,
          ease: 'back.out'
      });
  });

  // Header background on scroll
  ScrollTrigger.create({
    start: "top -80",
    end: 99999,
    toggleClass: {
      className: 'header-scrolled',
      targets: 'header'
    }
  });

  // --- Existing animations (from earlier) ---

  // About Section
  gsap.from("#about h2", {
    scrollTrigger: {
      trigger: "#about",
      start: "top 80%",
    },
    y: 50,
    opacity: 0,
    duration: 1
  });

  gsap.from(".about-left p", {
    scrollTrigger: {
      trigger: "#about",
      start: "top 75%",
    },
    y: 50,
    opacity: 0,
    duration: 1,
    stagger: 0.2,
    ease: "power3.out"
  });

  // BMI Calculator
  const calculateBmiBtn = document.getElementById('calculate-bmi');
  const resetBmiBtn = document.getElementById('reset-bmi');
  const bmiResult = document.getElementById('bmi-result');
  const bmiValue = document.getElementById('bmi-value');
  const bmiCategory = document.getElementById('bmi-category');
  const bmiInfo = document.getElementById('bmi-info');
  
  // Unit toggle elements
  const unitBtns = document.querySelectorAll('.unit-btn');
  const metricInputs = document.getElementById('metric-inputs');
  const imperialInputs = document.getElementById('imperial-inputs');
  
  // Metric inputs
  const heightCm = document.getElementById('height-cm');
  const weightKg = document.getElementById('weight-kg');
  
  // Imperial inputs
  const heightFeet = document.getElementById('height-feet');
  const heightInches = document.getElementById('height-inches');
  const weightLbs = document.getElementById('weight-lbs');

  let currentUnit = 'metric';

  // Unit toggle functionality
  unitBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      unitBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      currentUnit = btn.getAttribute('data-unit');
      
      if (currentUnit === 'metric') {
        metricInputs.style.display = 'block';
        imperialInputs.style.display = 'none';
        heightCm.focus();
      } else {
        metricInputs.style.display = 'none';
        imperialInputs.style.display = 'block';
        heightFeet.focus();
      }
      
      bmiResult.style.display = 'none';
    });
  });

  function calculateBMI() {
    let height, weight;

    if (currentUnit === 'metric') {
      height = parseFloat(heightCm.value);
      weight = parseFloat(weightKg.value);

      if (!height || !weight || height <= 0 || weight <= 0) {
        alert('Please enter valid height and weight values');
        return;
      }

      const heightInMeters = height / 100;
      const bmi = weight / (heightInMeters * heightInMeters);
      displayBMIResult(bmi);
    } else {
      const feet = parseFloat(heightFeet.value);
      const inches = parseFloat(heightInches.value) || 0;
      weight = parseFloat(weightLbs.value);

      if (!feet || weight <= 0 || feet < 0 || inches < 0) {
        alert('Please enter valid height and weight values');
        return;
      }

      // Convert feet and inches to total inches
      const totalInches = feet * 12 + inches;
      
      // BMI formula: (weight in pounds * 703) / (height in inches)^2
      const bmi = (weight * 703) / (totalInches * totalInches);
      displayBMIResult(bmi);
    }
  }

  function displayBMIResult(bmi) {
    const bmiRounded = bmi.toFixed(1);
    bmiValue.textContent = bmiRounded;

    let category = '';
    let info = '';
    let className = '';

    if (bmi < 18.5) {
      category = 'UNDERWEIGHT';
      info = 'You are underweight. Consider consulting with a fitness professional to develop a healthy training plan.';
      className = 'underweight';
    } else if (bmi < 25) {
      category = 'NORMAL WEIGHT';
      info = 'Great! You have a healthy weight. Focus on maintaining through consistent training and proper nutrition.';
      className = 'normal';
    } else if (bmi < 30) {
      category = 'OVERWEIGHT';
      info = 'You are overweight. Our programs can help you achieve your fitness goals through structured training.';
      className = 'overweight';
    } else {
      category = 'OBESE';
      info = 'Start your transformation journey with us. Our movement fundamentals program is perfect for getting started.';
      className = 'obese';
    }

    bmiCategory.textContent = category;
    bmiCategory.className = 'bmi-category ' + className;
    bmiInfo.textContent = info;

    bmiResult.style.display = 'block';

    gsap.from(bmiResult, {
      opacity: 0,
      scale: 0.9,
      duration: 0.6,
      ease: 'back.out'
    });
  }

  function resetBMI() {
    heightCm.value = '';
    weightKg.value = '';
    heightFeet.value = '';
    heightInches.value = '';
    weightLbs.value = '';
    bmiResult.style.display = 'none';
    bmiValue.textContent = '0';
    bmiCategory.textContent = 'Enter your details';
    bmiCategory.className = 'bmi-category';
    bmiInfo.textContent = '';
    
    if (currentUnit === 'metric') {
      heightCm.focus();
    } else {
      heightFeet.focus();
    }
  }

  calculateBmiBtn.addEventListener('click', calculateBMI);
  resetBmiBtn.addEventListener('click', resetBMI);

  // Enter key support for metric inputs
  heightCm.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') calculateBMI();
  });

  weightKg.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') calculateBMI();
  });

  // Enter key support for imperial inputs
  heightFeet.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') heightInches.focus();
  });

  heightInches.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') calculateBMI();
  });

  weightLbs.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') calculateBMI();
  });

  gsap.from("#bmi-calculator h2", {
    scrollTrigger: {
      trigger: "#bmi-calculator",
      start: "top 80%",
    },
    y: 50,
    opacity: 0,
    duration: 1
  });

  gsap.from(".bmi-container", {
    scrollTrigger: {
      trigger: ".bmi-container",
      start: "top center",
      toggleActions: "play none none reverse"
    },
    y: 100,
    opacity: 0,
    duration: 1,
    stagger: 0.2,
    ease: "power3.out"
  });

  // Testimonials
  gsap.from("#testimonials h2", {
    scrollTrigger: {
      trigger: "#testimonials",
      start: "top 80%",
    },
    y: 40,
    opacity: 0,
    duration: 1
  });

  gsap.from(".testimonial-slider", {
    scrollTrigger: {
      trigger: ".testimonial-slider",
      start: "top 85%",
    },
    scale: 0.9,
    opacity: 0,
    duration: 1.2,
    ease: "back.out(1.7)"
  });

  // Contact
  gsap.from("#contact h2", {
    scrollTrigger: {
      trigger: "#contact",
      start: "top 80%",
    },
    y: 40,
    opacity: 0,
    duration: 1
  });

  gsap.from("#contact form", {
    scrollTrigger: {
      trigger: "#contact form",
      start: "top 85%",
    },
    y: 80,
    opacity: 0,
    duration: 1,
    ease: "power2.out"
  });

  // Footer
  gsap.from("#footer .footer-content", {
    scrollTrigger: {
      trigger: "#footer",
      start: "top 85%",
    },
    y: 60,
    opacity: 0,
    duration: 1.2,
    ease: "power2.out"
  });

  // --- Parallax Backgrounds ---
  const parallaxSections = [".testimonials", ".contact", "#footer"];

  parallaxSections.forEach(section => {
    gsap.to(section, {
      backgroundPosition: "50% 100%", // shifts bg down as you scroll
      ease: "none",
      scrollTrigger: {
        trigger: section,
        start: "top bottom",  // start when section enters view
        end: "bottom top",    // end when section leaves view
        scrub: true           // smooth scroll-linked animation
      }
    });
  });

  // --- Header Scroll Effect ---
  const header = document.querySelector('header');

  window.addEventListener('scroll', () => {
      if (window.scrollY > 50) {
          header.classList.add('scrolled');
      } else {
          header.classList.remove('scrolled');
      }
  });

  // Hero animations
  const tl = gsap.timeline();
  
  tl.to(".hero-title .line", {
      y: 0,
      opacity: 1,
      duration: 1.2,
      ease: "power4.out",
      stagger: 0.2
  })
  .to(".hero-subtitle", {
      opacity: 1,
      duration: 1,
      ease: "power3.out"
  }, "-=0.8")
  .to(".cta-button", {
      opacity: 1,
      duration: 1,
      ease: "power3.out"
  }, "-=0.8");

  // Contact Form Handler with FastAPI
  const contactForm = document.getElementById('contact-form');
  const contactResponse = document.getElementById('contact-response');
  const responseText = document.getElementById('response-text');

  if (contactForm) {
    contactForm.addEventListener('submit', async (e) => {
      e.preventDefault();

      const name = document.getElementById('contact-name').value;
      const email = document.getElementById('contact-email').value;
      const message = document.getElementById('contact-message').value;

      try {
        // Send data to FastAPI backend
        const response = await fetch('http://localhost:8000/api/contact', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            name: name,
            email: email,
            message: message
          })
        });

        const data = await response.json();

        if (response.ok) {
          // Show success message
          responseText.textContent = data.message;
          contactResponse.style.display = 'block';

          // Animate the response message
          gsap.from('#contact-response', {
            opacity: 0,
            scale: 0.9,
            duration: 0.5,
            ease: 'back.out'
          });

          // Clear the form
          contactForm.reset();

          // Hide the response message after 5 seconds
          setTimeout(() => {
            gsap.to('#contact-response', {
              opacity: 0,
              scale: 0.9,
              duration: 0.5,
              ease: 'back.in',
              onComplete: () => {
                contactResponse.style.display = 'none';
              }
            });
          }, 5000);
        } else {
          responseText.textContent = 'Error: ' + (data.detail || 'Failed to send message');
          contactResponse.classList.add('error');
          contactResponse.style.display = 'block';
        }
      } catch (error) {
        responseText.textContent = 'Error: Could not connect to server. Make sure FastAPI is running.';
        contactResponse.classList.add('error');
        contactResponse.style.display = 'block';
        console.error('Error:', error);
      }
    });
  }
});