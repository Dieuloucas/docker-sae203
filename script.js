// ── Navbar scroll effect + lien actif ────────────────────────────────────────
const navbar = document.getElementById('navbar');
const sections = document.querySelectorAll('section[id]');
const navLinks = document.querySelectorAll('.nav-links a');

window.addEventListener('scroll', () => {
  // Ajoute "scrolled" quand on descend de plus de 40px (shadow sur la navbar)
  navbar.classList.toggle('scrolled', window.scrollY > 40);

  // Parcourt toutes les sections pour trouver celle visible
  let current = '';
  sections.forEach(s => {
    if (window.scrollY >= s.offsetTop - 120) current = s.id;
  });

  // Met "active" sur le lien navbar correspondant à la section visible
  navLinks.forEach(a => {
    a.classList.toggle('active', a.getAttribute('href') === '#' + current);
  });
});

// ── Menu burger (mobile) ─────────────────────────────────────────────────────
document.getElementById('burger').addEventListener('click', () => {
  document.querySelector('.nav-links').classList.toggle('open');
});

// ── Reveal on scroll (animation d'apparition) ────────────────────────────────
const revealEls = document.querySelectorAll(
  '.card, .feature-group, .step, .arch-layer, .detail-block'
);

// IntersectionObserver : surveille quand un élément entre dans le viewport
const observer = new IntersectionObserver(entries => {
  entries.forEach(e => {
    if (e.isIntersecting) {          // élément maintenant visible
      e.target.style.opacity = '1';
      e.target.style.transform = 'translateY(0)';
      observer.unobserve(e.target);  // arrête de surveiller cet élément
    }
  });
}, { threshold: 0.1 }); // déclenche à 10% de visibilité

revealEls.forEach(el => {
  el.style.opacity = '0';
  el.style.transform = 'translateY(24px)';
  el.style.transition = 'opacity .5s ease, transform .5s ease';
  observer.observe(el);
});
