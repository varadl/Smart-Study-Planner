/**
 * Smart Study Planner – Custom JavaScript
 * Handles: form validation, password toggle, strength meter, progress animation
 */

/* ═══════════════════════════════════════════════════════════════
   1. DOM READY INIT
   ═══════════════════════════════════════════════════════════════ */
document.addEventListener('DOMContentLoaded', () => {
  initFormValidation();
  initPasswordToggle();
  initPasswordStrength();
  initProgressBarAnimation();
  initAutoHideAlerts();
  initSubjectDateMin();
  initExamDateMin();
  initConfirmPasswordValidation();
  initProfilePasswordValidation();
});

/* ═══════════════════════════════════════════════════════════════
   2. BOOTSTRAP FORM VALIDATION
   ═══════════════════════════════════════════════════════════════ */
function initFormValidation() {
  const forms = document.querySelectorAll('form[id]');
  forms.forEach(form => {
    form.addEventListener('submit', e => {
      if (!form.checkValidity()) {
        e.preventDefault();
        e.stopPropagation();
      }
      form.classList.add('was-validated');
    });
  });
}

/* ═══════════════════════════════════════════════════════════════
   3. SHOW / HIDE PASSWORD TOGGLE
   ═══════════════════════════════════════════════════════════════ */
function initPasswordToggle() {
  document.querySelectorAll('.toggle-pw').forEach(btn => {
    btn.addEventListener('click', () => {
      const targetId = btn.getAttribute('data-target');
      const input    = document.getElementById(targetId);
      const icon     = btn.querySelector('i');
      if (!input) return;

      if (input.type === 'password') {
        input.type = 'text';
        icon.classList.replace('bi-eye', 'bi-eye-slash');
      } else {
        input.type = 'password';
        icon.classList.replace('bi-eye-slash', 'bi-eye');
      }
    });
  });
}

/* ═══════════════════════════════════════════════════════════════
   4. PASSWORD STRENGTH METER
   ═══════════════════════════════════════════════════════════════ */
function initPasswordStrength() {
  const pwField = document.getElementById('reg_password');
  const bar     = document.getElementById('strengthBar');
  const label   = document.getElementById('strengthLabel');
  if (!pwField || !bar || !label) return;

  pwField.addEventListener('input', () => {
    const pw  = pwField.value;
    let score = 0;

    if (pw.length >= 6)                    score++;
    if (pw.length >= 10)                   score++;
    if (/[A-Z]/.test(pw))                  score++;
    if (/[0-9]/.test(pw))                  score++;
    if (/[^A-Za-z0-9]/.test(pw))           score++;

    const levels = [
      { pct: 0,   cls: '',          text: '' },
      { pct: 20,  cls: 'bg-danger', text: 'Very Weak' },
      { pct: 40,  cls: 'bg-warning', text: 'Weak' },
      { pct: 60,  cls: 'bg-info',   text: 'Fair' },
      { pct: 80,  cls: 'bg-primary', text: 'Strong' },
      { pct: 100, cls: 'bg-success', text: 'Very Strong 💪' }
    ];

    const lvl = levels[score] || levels[0];
    bar.style.width = lvl.pct + '%';
    bar.className   = 'progress-bar ' + lvl.cls;
    label.textContent = pw.length > 0 ? `Strength: ${lvl.text}` : '';
    label.style.color = score >= 4 ? 'var(--success)' : score >= 2 ? 'var(--warning)' : 'var(--danger)';
  });
}

/* ═══════════════════════════════════════════════════════════════
   5. CONFIRM PASSWORD VALIDATION
   ═══════════════════════════════════════════════════════════════ */
function initConfirmPasswordValidation() {
  const pw1  = document.getElementById('reg_password');
  const pw2  = document.getElementById('reg_confirm');
  const form = document.getElementById('registerForm');
  if (!pw1 || !pw2 || !form) return;

  function checkMatch() {
    if (pw2.value && pw1.value !== pw2.value) {
      pw2.setCustomValidity('Passwords do not match.');
    } else {
      pw2.setCustomValidity('');
    }
  }

  pw1.addEventListener('input', checkMatch);
  pw2.addEventListener('input', checkMatch);
}

/* ═══════════════════════════════════════════════════════════════
   6. ANIMATE PROGRESS BAR (Dashboard)
   ═══════════════════════════════════════════════════════════════ */
function initProgressBarAnimation() {
  const bar = document.getElementById('overallProgress');
  if (!bar) return;
  const target = parseFloat(bar.getAttribute('data-target')) || 0;

  // Animate from 0 → target
  setTimeout(() => { bar.style.width = target + '%'; }, 300);

  // Color coding by completion %
  if (target >= 80) {
    bar.classList.add('bg-success');
  } else if (target >= 50) {
    bar.classList.add('bg-primary');
  } else if (target >= 25) {
    bar.classList.add('bg-warning');
  } else {
    bar.classList.add('bg-danger');
  }
}

/* ═══════════════════════════════════════════════════════════════
   7. AUTO-HIDE FLASH ALERTS (after 5 s)
   ═══════════════════════════════════════════════════════════════ */
function initAutoHideAlerts() {
  setTimeout(() => {
    document.querySelectorAll('#flash-container .alert').forEach(alert => {
      const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
      bsAlert.close();
    });
  }, 5000);
}

/* ═══════════════════════════════════════════════════════════════
   8. SET MINIMUM DATE ON EXAM DATE FIELDS (today onwards)
   ═══════════════════════════════════════════════════════════════ */
function initSubjectDateMin() {
  const examField = document.getElementById('exam_date');
  if (!examField) return;
  const today = new Date().toISOString().split('T')[0];
  examField.setAttribute('min', today);
}

function initExamDateMin() {
  // Same as above but catches any other date fields
  document.querySelectorAll('input[type="date"]').forEach(field => {
    if (!field.getAttribute('min')) {
      const today = new Date().toISOString().split('T')[0];
      field.setAttribute('min', today);
    }
  });
}

/* ═══════════════════════════════════════════════════════════════
   9. GENERATE PLAN BUTTON – loading state (non-form link version)
   ═══════════════════════════════════════════════════════════════ */
document.addEventListener('DOMContentLoaded', () => {
  const genBtn = document.getElementById('generatePlanBtn');
  if (genBtn) {
    genBtn.addEventListener('click', function (e) {
      // The click itself navigates via href; we just update the text visually
      setTimeout(() => {
        genBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Generating…';
        genBtn.classList.add('disabled');
      }, 10);
    });
  }
});
/* ═══════════════════════════════════════════════════════════════
   10. PROFILE – confirm new password check
   ═══════════════════════════════════════════════════════════════ */
function initProfilePasswordValidation() {
  const pw1  = document.getElementById('new_password');
  const pw2  = document.getElementById('confirm_password');
  if (!pw1 || !pw2) return;

  function checkMatch() {
    if (pw2.value && pw1.value !== pw2.value) {
      pw2.setCustomValidity('Passwords do not match.');
    } else {
      pw2.setCustomValidity('');
    }
  }
  pw1.addEventListener('input', checkMatch);
  pw2.addEventListener('input', checkMatch);
}
