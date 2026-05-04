// static/script.js — BuildAI Pro shared scripts

// ── Smooth scroll for anchor links ──────────────────────
document.querySelectorAll('a[href^="#"]').forEach(a => {
  a.addEventListener('click', e => {
    const target = document.querySelector(a.getAttribute('href'));
    if (target) { e.preventDefault(); target.scrollIntoView({ behavior: 'smooth' }); }
  });
});

// ── Animate number counters on results page ──────────────
function animateCounters() {
  document.querySelectorAll('.w-num').forEach(el => {
    const target = parseInt(el.textContent, 10);
    if (isNaN(target)) return;
    let current = 0;
    const step  = Math.ceil(target / 30);
    const timer = setInterval(() => {
      current = Math.min(current + step, target);
      el.textContent = current;
      if (current >= target) clearInterval(timer);
    }, 30);
  });
}

// ── Score bar fill animation ─────────────────────────────
function animateScoreBar() {
  const fill = document.querySelector('.score-fill');
  if (!fill) return;
  const w = fill.style.width;
  fill.style.width = '0';
  setTimeout(() => { fill.style.width = w; }, 200);
}

// ── Card entrance animation ──────────────────────────────
function animateCards() {
  const cards = document.querySelectorAll('.card, .ai-card, .blueprint-wrap, .sched-wrap');
  cards.forEach((card, i) => {
    card.style.opacity    = '0';
    card.style.transform  = 'translateY(18px)';
    card.style.transition = `opacity .4s ease ${i * 0.06}s, transform .4s ease ${i * 0.06}s`;
    setTimeout(() => {
      card.style.opacity   = '1';
      card.style.transform = 'translateY(0)';
    }, 80 + i * 60);
  });
}

// ── Form loading state ───────────────────────────────────
const form = document.querySelector('form[action="/calculate"]');
if (form) {
  form.addEventListener('submit', () => {
    const btn = form.querySelector('button[type="submit"]');
    if (btn) {
      btn.textContent = '⏳ Generating Plan...';
      btn.disabled    = true;
      btn.style.opacity = '0.75';
    }
  });
}

// ── Run on load ──────────────────────────────────────────
window.addEventListener('load', () => {
  animateCards();
  animateCounters();
  animateScoreBar();
});