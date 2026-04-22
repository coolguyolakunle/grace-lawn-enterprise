/* ── PAGE TRANSITION OVERLAY ──────────────────────────────── */
(function () {
  // Inject overlay once
  const overlay = document.createElement('div');
  overlay.id = 'page-overlay';
  overlay.style.cssText = `
    position:fixed; inset:0; z-index:9999;
    background: #1a4a2e;
    display:flex; align-items:center; justify-content:center;
    pointer-events:none;
    transition: opacity 0.45s cubic-bezier(.4,0,.2,1);
    opacity:0;
  `;
  overlay.innerHTML = `
    <div style="text-align:center; color:#fff; opacity:0; transition: opacity 0.3s 0.05s;">
      <div style="width:44px;height:44px;border:3px solid #5bbf85;border-top-color:transparent;
           border-radius:50%;animation:spin .7s linear infinite;margin:0 auto 12px;"></div>
      <p style="font-family:'Playfair Display',serif;font-size:1rem;color:#5bbf85;letter-spacing:.1em;">Grace Lawn</p>
    </div>
  `;
  document.body.appendChild(overlay);

  // Spin keyframe
  if (!document.getElementById('gl-keyframes')) {
    const s = document.createElement('style');
    s.id = 'gl-keyframes';
    s.textContent = `@keyframes spin{to{transform:rotate(360deg)}}`;
    document.head.appendChild(s);
  }

  // Fade in on load
  window.addEventListener('load', () => {
    overlay.style.opacity = '0';
    overlay.querySelector('div').style.opacity = '0';
  });

  // Intercept all internal links
  document.addEventListener('click', (e) => {
    const a = e.target.closest('a[href]');
    if (!a) return;
    const href = a.getAttribute('href');
    // Skip external, anchor, mailto, tel links
    if (!href || href.startsWith('#') || href.startsWith('http') ||
        href.startsWith('mailto') || href.startsWith('tel') ||
        a.target === '_blank') return;

    e.preventDefault();
    overlay.style.opacity = '1';
    overlay.querySelector('div').style.opacity = '1';
    overlay.style.pointerEvents = 'all';

    setTimeout(() => {
      window.location.href = href;
    }, 420);
  });

  // Fade out overlay on pageshow (back/forward cache)
  window.addEventListener('pageshow', () => {
    overlay.style.opacity = '0';
    overlay.style.pointerEvents = 'none';
  });
})();


/* ── NAVBAR: SCROLL SHRINK + HIDE/SHOW ─── */
(function () {
  const nav = document.querySelector('nav');
  if (!nav) return;
  let lastY = 0;
  let ticking = false;

  window.addEventListener('scroll', () => {
    if (!ticking) {
      requestAnimationFrame(() => {
        const y = window.scrollY;
        // Shrink on scroll
        if (y > 60) {
          nav.style.boxShadow = '0 4px 24px rgba(26,74,46,0.12)';
          nav.style.background = 'rgba(255,255,255,0.98)';
        } else {
          nav.style.boxShadow = '';
          nav.style.background = '';
        }
        // Hide on scroll down, show on scroll up
        if (y > lastY + 8 && y > 120) {
          nav.style.transform = 'translateY(-100%)';
          nav.style.transition = 'transform 0.35s cubic-bezier(.4,0,.2,1), box-shadow 0.3s, background 0.3s';
        } else if (y < lastY - 4) {
          nav.style.transform = 'translateY(0)';
        }
        lastY = y;
        ticking = false;
      });
      ticking = true;
    }
  });
})();


/* ── MOBILE MENU TOGGLE ──── */
(function () {
  const toggle = document.getElementById('menu-toggle');
  const menu   = document.getElementById('mobile-menu');
  const icon   = document.getElementById('menu-icon');
  if (!toggle || !menu) return;

  // Override inline display:none with height-based animation
  menu.style.cssText = `
    overflow:hidden; max-height:0;
    transition: max-height 0.38s cubic-bezier(.4,0,.2,1), opacity 0.3s;
    opacity:0; display:block !important;
  `;

  toggle.addEventListener('click', () => {
    const isOpen = menu.dataset.open === '1';
    if (isOpen) {
      menu.style.maxHeight = '0';
      menu.style.opacity   = '0';
      menu.dataset.open    = '0';
      icon.classList.replace('fa-times', 'fa-bars');
    } else {
      menu.style.maxHeight = menu.scrollHeight + 'px';
      menu.style.opacity   = '1';
      menu.dataset.open    = '1';
      icon.classList.replace('fa-bars', 'fa-times');
    }
  });
})();


/* ── SCROLL REVEAL (staggered) ────── */
(function () {
  const els = document.querySelectorAll('.reveal');
  if (!els.length) return;

  // Group siblings for stagger
  els.forEach((el, i) => {
    const siblings = el.parentElement
      ? Array.from(el.parentElement.querySelectorAll(':scope > .reveal'))
      : [];
    const idx = siblings.indexOf(el);
    el.style.transitionDelay = idx > 0 ? `${idx * 0.1}s` : '0s';
  });

  const io = new IntersectionObserver((entries) => {
    entries.forEach(e => {
      if (e.isIntersecting) {
        e.target.classList.add('visible');
        io.unobserve(e.target);
      }
    });
  }, { threshold: 0.1 });

  els.forEach(el => io.observe(el));
})();


/* ── SMOOTH SCROLL FOR ANCHOR LINKS ──── */
document.querySelectorAll('a[href^="#"]').forEach(a => {
  a.addEventListener('click', e => {
    const id = a.getAttribute('href').slice(1);
    const target = document.getElementById(id);
    if (target) {
      e.preventDefault();
      target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  });
});


/* ── COUNTER ANIMATION (stats strip) ────── */
(function () {
  const counters = document.querySelectorAll('[data-count]');
  if (!counters.length) return;

  const io = new IntersectionObserver((entries) => {
    entries.forEach(e => {
      if (!e.isIntersecting) return;
      const el  = e.target;
      const end = parseInt(el.dataset.count, 10);
      const dur = 1400;
      const step = 16;
      let current = 0;
      const increment = end / (dur / step);
      const suffix = el.dataset.suffix || '';

      const tick = () => {
        current = Math.min(current + increment, end);
        el.textContent = Math.floor(current).toLocaleString() + suffix;
        if (current < end) requestAnimationFrame(tick);
      };
      requestAnimationFrame(tick);
      io.unobserve(el);
    });
  }, { threshold: 0.5 });

  counters.forEach(c => io.observe(c));
})();


/* ── GALLERY FILTER (with fade animation) ───── */
(function () {
  const btns  = document.querySelectorAll('.filter-btn');
  const items = document.querySelectorAll('.gallery-item');
  if (!btns.length) return;

  btns.forEach(btn => {
    btn.addEventListener('click', () => {
      // Button styles
      btns.forEach(b => {
        b.classList.remove('bg-deep-green', 'text-white');
        b.classList.add('text-deep-green');
      });
      btn.classList.add('bg-deep-green', 'text-white');
      btn.classList.remove('text-deep-green');

      const filter = btn.dataset.filter;

      items.forEach((item, i) => {
        const match = filter === 'all' || item.dataset.category === filter;
        if (match) {
          item.style.display = 'block';
          item.style.opacity = '0';
          item.style.transform = 'scale(0.92)';
          // Staggered entrance
          setTimeout(() => {
            item.style.transition = 'opacity 0.35s ease, transform 0.35s ease';
            item.style.opacity    = '1';
            item.style.transform  = 'scale(1)';
          }, i * 40);
        } else {
          item.style.transition = 'opacity 0.2s ease';
          item.style.opacity    = '0';
          setTimeout(() => { item.style.display = 'none'; }, 200);
        }
      });
    });
  });
})();


/* ── CONTACT FORM FEEDBACK ──────── */
(function () {
  const form = document.getElementById('contact-form');
  if (!form) return;

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    const btn = form.querySelector('button[type="submit"]');
    const msg = document.getElementById('form-success');

    btn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Sending…';
    btn.disabled  = true;
    btn.style.opacity = '0.7';

    // Simulate send (replace with real fetch to Flask route)
    setTimeout(() => {
      btn.innerHTML = '<i class="fas fa-check mr-2"></i>Message Sent!';
      btn.style.background = '#2d7a4f';
      btn.style.opacity = '1';

      if (msg) {
        msg.classList.remove('hidden');
        msg.style.animation = 'fadeInUp 0.4s ease forwards';
      }

      // Reset after 4s
      setTimeout(() => {
        btn.innerHTML = '<i class="fas fa-paper-plane mr-2"></i>Send Message';
        btn.style.background = '';
        btn.disabled = false;
        if (msg) msg.classList.add('hidden');
        form.reset();
      }, 4000);
    }, 1600);
  });
})();


/* ── TOOLTIP ON BREED CARDS ─────── */
(function () {
  // Add subtle pulse to feature cards on hover
  document.querySelectorAll('.feature-card').forEach(card => {
    card.addEventListener('mouseenter', () => {
      card.style.transition = 'transform 0.3s cubic-bezier(.34,1.56,.64,1), box-shadow 0.3s';
    });
  });
})();


/* ── ACTIVE NAV LINK HIGHLIGHT ─────── */
(function () {
  const path = window.location.pathname;
  document.querySelectorAll('.nav-link').forEach(a => {
    const href = a.getAttribute('href');
    if (href && path === href) {
      a.classList.add('active');
    }
  });
})();


/* ── BACK TO TOP BUTTON ─────── */
(function () {
  const btn = document.createElement('button');
  btn.id = 'back-to-top';
  btn.innerHTML = '<i class="fas fa-chevron-up"></i>';
  btn.style.cssText = `
    position:fixed; bottom:28px; right:28px; z-index:999;
    width:44px; height:44px; border-radius:50%;
    background:#1a4a2e; color:#5bbf85;
    border:none; cursor:pointer; font-size:1rem;
    box-shadow: 0 4px 16px rgba(26,74,46,0.25);
    opacity:0; transform:translateY(12px);
    transition: opacity 0.3s, transform 0.3s, background 0.2s;
    display:flex; align-items:center; justify-content:center;
  `;
  document.body.appendChild(btn);

  window.addEventListener('scroll', () => {
    if (window.scrollY > 400) {
      btn.style.opacity   = '1';
      btn.style.transform = 'translateY(0)';
    } else {
      btn.style.opacity   = '0';
      btn.style.transform = 'translateY(12px)';
    }
  });

  btn.addEventListener('click', () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  });

  btn.addEventListener('mouseenter', () => { btn.style.background = '#2d7a4f'; });
  btn.addEventListener('mouseleave', () => { btn.style.background = '#1a4a2e'; });
})();


/* ── HERO TEXT ENTRANCE ────────── */
(function () {
  const heroChildren = document.querySelectorAll('.hero-entrance > *');
  heroChildren.forEach((el, i) => {
    el.style.opacity   = '0';
    el.style.transform = 'translateY(24px)';
    el.style.transition = `opacity 0.6s ease ${i * 0.12}s, transform 0.6s ease ${i * 0.12}s`;
    requestAnimationFrame(() => {
      requestAnimationFrame(() => {
        el.style.opacity   = '1';
        el.style.transform = 'translateY(0)';
      });
    });
  });
})();
