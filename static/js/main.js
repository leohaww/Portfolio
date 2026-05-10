/* ============================================================
   ENTERPRISE PORTFOLIO — main.js  v2.0  FUTURISTIC EDITION
   Features: Particle canvas · Cursor glow · HUD scan lines
             Nav scroll · Reveal · Counter · Skill bars
             Skills filter · Admin sidebar · Toast dismiss
             Typewriter · Tilt cards · Magnetic buttons
   ============================================================ */

(function () {
  "use strict";

  /* ─────────────────────────────────────────────
     1. PARTICLE CANVAS (hero background)
  ───────────────────────────────────────────── */
  function initParticles() {
    const hero = document.querySelector(".hero");
    if (!hero) return;

    const canvas = document.createElement("canvas");
    canvas.style.cssText = "position:absolute;inset:0;pointer-events:none;z-index:0;opacity:0.55;";
    hero.insertBefore(canvas, hero.firstChild);

    const ctx = canvas.getContext("2d");
    let W, H, particles = [], mouse = { x: -999, y: -999 };
    const COUNT = window.innerWidth < 768 ? 40 : 90;
    const COLORS = ["rgba(139,92,246,", "rgba(0,245,255,", "rgba(167,139,250,"];

    function resize() {
      W = canvas.width  = hero.offsetWidth;
      H = canvas.height = hero.offsetHeight;
    }

    function Particle() {
      this.x = Math.random() * W;
      this.y = Math.random() * H;
      this.vx = (Math.random() - .5) * .6;
      this.vy = (Math.random() - .5) * .6;
      this.r  = Math.random() * 1.5 + .4;
      this.alpha = Math.random() * .6 + .2;
      this.color = COLORS[Math.floor(Math.random() * COLORS.length)];
      this.pulse = Math.random() * Math.PI * 2;
    }

    Particle.prototype.draw = function () {
      this.pulse += .02;
      const a = this.alpha * (.7 + .3 * Math.sin(this.pulse));
      ctx.beginPath();
      ctx.arc(this.x, this.y, this.r, 0, Math.PI * 2);
      ctx.fillStyle = this.color + a + ")";
      ctx.fill();
    };

    Particle.prototype.update = function () {
      this.x += this.vx;
      this.y += this.vy;
      if (this.x < 0 || this.x > W) this.vx *= -1;
      if (this.y < 0 || this.y > H) this.vy *= -1;
      // Mouse repulsion
      const dx = this.x - mouse.x;
      const dy = this.y - mouse.y;
      const dist = Math.sqrt(dx * dx + dy * dy);
      if (dist < 100) {
        this.x += dx / dist * 1.5;
        this.y += dy / dist * 1.5;
      }
    };

    function drawLines() {
      for (let i = 0; i < particles.length; i++) {
        for (let j = i + 1; j < particles.length; j++) {
          const dx = particles[i].x - particles[j].x;
          const dy = particles[i].y - particles[j].y;
          const d  = Math.sqrt(dx * dx + dy * dy);
          if (d < 120) {
            ctx.beginPath();
            ctx.moveTo(particles[i].x, particles[i].y);
            ctx.lineTo(particles[j].x, particles[j].y);
            ctx.strokeStyle = `rgba(139,92,246,${(1 - d / 120) * 0.18})`;
            ctx.lineWidth = .5;
            ctx.stroke();
          }
        }
      }
    }

    function init() {
      resize();
      particles = [];
      for (let i = 0; i < COUNT; i++) particles.push(new Particle());
    }

    function loop() {
      ctx.clearRect(0, 0, W, H);
      drawLines();
      particles.forEach(p => { p.update(); p.draw(); });
      requestAnimationFrame(loop);
    }

    hero.addEventListener("mousemove", e => {
      const rect = hero.getBoundingClientRect();
      mouse.x = e.clientX - rect.left;
      mouse.y = e.clientY - rect.top;
    });
    hero.addEventListener("mouseleave", () => { mouse.x = -999; mouse.y = -999; });
    window.addEventListener("resize", () => { init(); });

    init();
    loop();
  }

  /* ─────────────────────────────────────────────
     2. CURSOR GLOW  (desktop only)
  ───────────────────────────────────────────── */
  function initCursorGlow() {
    if (window.innerWidth < 768) return;
    const glow = document.createElement("div");
    glow.style.cssText = `
      position:fixed;width:400px;height:400px;border-radius:50%;
      background:radial-gradient(circle,rgba(139,92,246,0.06) 0%,transparent 70%);
      pointer-events:none;z-index:0;transform:translate(-50%,-50%);
      transition:opacity .4s ease;
    `;
    document.body.appendChild(glow);

    let cx = 0, cy = 0, tx = 0, ty = 0;
    window.addEventListener("mousemove", e => { tx = e.clientX; ty = e.clientY; });
    window.addEventListener("mouseleave", () => { glow.style.opacity = "0"; });
    window.addEventListener("mouseenter", () => { glow.style.opacity = "1"; });

    function trackCursor() {
      cx += (tx - cx) * .1;
      cy += (ty - cy) * .1;
      glow.style.left = cx + "px";
      glow.style.top  = cy + "px";
      requestAnimationFrame(trackCursor);
    }
    trackCursor();
  }

  /* ─────────────────────────────────────────────
     3. TYPEWRITER  (hero title)
  ───────────────────────────────────────────── */
  function initTypewriter() {
    const el = document.querySelector(".hero__title");
    if (!el) return;
    const text   = el.textContent.trim();
    const cursor = document.createElement("span");
    cursor.style.cssText = "border-right:2px solid var(--cyan);margin-left:2px;animation:neonPulse 1s infinite;display:inline-block;";
    el.textContent = "";
    el.appendChild(cursor);

    let i = 0;
    const delay = 2200; // start after page loads

    function type() {
      if (i < text.length) {
        el.insertBefore(document.createTextNode(text[i]), cursor);
        i++;
        setTimeout(type, 60 + Math.random() * 40);
      }
    }
    setTimeout(type, delay);
  }

  /* ─────────────────────────────────────────────
     4. NAVBAR scroll + active link
  ───────────────────────────────────────────── */
  function initNav() {
    const nav = document.getElementById("mainNav");
    if (nav) {
      window.addEventListener("scroll", () => {
        nav.classList.toggle("nav--scrolled", window.scrollY > 50);
      }, { passive: true });
    }

    // Active section highlight
    const sections = document.querySelectorAll("section[id]");
    const links    = document.querySelectorAll(".nav__link");
    if (sections.length && links.length) {
      const obs = new IntersectionObserver(entries => {
        entries.forEach(e => {
          if (e.isIntersecting) {
            links.forEach(l => {
              l.classList.toggle("nav__link--active", l.getAttribute("href") === "#" + e.target.id);
            });
          }
        });
      }, { rootMargin: "-40% 0px -55% 0px" });
      sections.forEach(s => obs.observe(s));
    }
  }

  /* ─────────────────────────────────────────────
     5. MOBILE DRAWER
  ───────────────────────────────────────────── */
  function initMobileNav() {
    const burger   = document.getElementById("hamburger");
    const drawer   = document.getElementById("navDrawer");
    const backdrop = document.getElementById("navBackdrop");
    if (!burger || !drawer) return;

    function close() {
      drawer.classList.remove("open");
      if (backdrop) backdrop.classList.remove("show");
      burger.setAttribute("aria-expanded", "false");
    }
    burger.addEventListener("click", () => {
      const open = drawer.classList.toggle("open");
      if (backdrop) backdrop.classList.toggle("show", open);
      burger.setAttribute("aria-expanded", String(open));
    });
    if (backdrop) backdrop.addEventListener("click", close);
    drawer.querySelectorAll("a").forEach(a => a.addEventListener("click", close));
  }

  /* ─────────────────────────────────────────────
     6. SMOOTH SCROLL
  ───────────────────────────────────────────── */
  function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(a => {
      a.addEventListener("click", e => {
        const target = document.querySelector(a.getAttribute("href"));
        if (!target) return;
        e.preventDefault();
        const top = target.getBoundingClientRect().top + window.scrollY - 80;
        window.scrollTo({ top, behavior: "smooth" });
      });
    });
  }

  /* ─────────────────────────────────────────────
     7. REVEAL ON SCROLL
  ───────────────────────────────────────────── */
  function initReveal() {
    const els = document.querySelectorAll(".reveal");
    if (!els.length) return;
    const obs = new IntersectionObserver((entries) => {
      entries.forEach((e, i) => {
        if (e.isIntersecting) {
          setTimeout(() => e.target.classList.add("visible"), i * 90);
          obs.unobserve(e.target);
        }
      });
    }, { threshold: 0.08 });
    els.forEach(el => obs.observe(el));
  }

  /* ─────────────────────────────────────────────
     8. COUNTER ANIMATION
  ───────────────────────────────────────────── */
  function initCounters() {
    document.querySelectorAll("[data-count]").forEach(el => {
      const target = parseInt(el.dataset.count, 10);
      if (isNaN(target)) return;
      const obs = new IntersectionObserver(entries => {
        if (!entries[0].isIntersecting) return;
        let count = 0;
        const step  = Math.max(1, Math.ceil(target / 70));
        const timer = setInterval(() => {
          count = Math.min(count + step, target);
          el.textContent = count.toLocaleString("id-ID");
          if (count >= target) clearInterval(timer);
        }, 22);
        obs.unobserve(el);
      });
      obs.observe(el);
    });
  }

  /* ─────────────────────────────────────────────
     9. SKILL BAR ANIMATION + FILTER TABS
  ───────────────────────────────────────────── */
  function initSkills() {
    // Animate bars on scroll
    const grid = document.getElementById("skillsGrid");
    if (grid) {
      const obs = new IntersectionObserver(entries => {
        if (entries[0].isIntersecting) {
          grid.querySelectorAll(".skill-card__fill").forEach((bar, i) => {
            setTimeout(() => { bar.style.width = bar.dataset.width; }, i * 60);
          });
          obs.unobserve(grid);
        }
      }, { threshold: 0.1 });
      obs.observe(grid);
    }

    // Filter tabs
    document.querySelectorAll(".skills__tab").forEach(tab => {
      tab.addEventListener("click", () => {
        document.querySelectorAll(".skills__tab").forEach(t => t.classList.remove("skills__tab--active"));
        tab.classList.add("skills__tab--active");
        const filter = tab.dataset.filter;
        document.querySelectorAll(".skill-card").forEach(card => {
          const show = filter === "all" || card.dataset.category === filter;
          card.style.display = show ? "flex" : "none";
          // Re-animate bars on filter
          if (show) {
            const fill = card.querySelector(".skill-card__fill");
            if (fill) { fill.style.width = "0%"; setTimeout(() => { fill.style.width = fill.dataset.width; }, 80); }
          }
        });
      });
    });
  }

  /* ─────────────────────────────────────────────
     10. TILT CARD EFFECT (project cards)
  ───────────────────────────────────────────── */
  function initTiltCards() {
    if (window.innerWidth < 768) return;
    document.querySelectorAll(".project-card").forEach(card => {
      card.addEventListener("mousemove", e => {
        const rect  = card.getBoundingClientRect();
        const cx    = rect.left + rect.width / 2;
        const cy    = rect.top  + rect.height / 2;
        const dx    = (e.clientX - cx) / (rect.width / 2);
        const dy    = (e.clientY - cy) / (rect.height / 2);
        card.style.transform = `translateY(-6px) rotateY(${dx * 5}deg) rotateX(${-dy * 4}deg)`;
        card.style.transition = "transform 0.1s ease";
      });
      card.addEventListener("mouseleave", () => {
        card.style.transform = "";
        card.style.transition = "transform 0.4s ease";
      });
    });
  }

  /* ─────────────────────────────────────────────
     11. MAGNETIC BUTTONS
  ───────────────────────────────────────────── */
  function initMagneticButtons() {
    if (window.innerWidth < 768) return;
    document.querySelectorAll(".btn--primary, .btn--outline").forEach(btn => {
      btn.addEventListener("mousemove", e => {
        const rect = btn.getBoundingClientRect();
        const dx   = e.clientX - (rect.left + rect.width / 2);
        const dy   = e.clientY - (rect.top + rect.height / 2);
        btn.style.transform = `translate(${dx * .2}px, ${dy * .3}px) translateY(-2px)`;
      });
      btn.addEventListener("mouseleave", () => {
        btn.style.transform = "";
      });
    });
  }

  /* ─────────────────────────────────────────────
     12. GLITCH TEXT EFFECT (section titles)
  ───────────────────────────────────────────── */
  function initGlitch() {
    const titles = document.querySelectorAll(".section__title");
    const chars  = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@#$%";

    titles.forEach(title => {
      const obs = new IntersectionObserver(entries => {
        if (!entries[0].isIntersecting) return;
        const orig = title.textContent;
        let iter = 0;
        const total = orig.length * 2.5;
        const interval = setInterval(() => {
          title.textContent = orig.split("").map((c, i) => {
            if (c === " ") return " ";
            if (i < iter / 2.5) return orig[i];
            return chars[Math.floor(Math.random() * chars.length)];
          }).join("");
          if (iter >= total) { title.textContent = orig; clearInterval(interval); }
          iter++;
        }, 35);
        obs.unobserve(title);
      }, { threshold: .5 });
      obs.observe(title);
    });
  }

  /* ─────────────────────────────────────────────
     13. HUD CORNER DECORATIONS
  ───────────────────────────────────────────── */
  function initHUDDecorations() {
    // Add corner brackets to glass cards
    document.querySelectorAll(".contact__form, .auth__card").forEach(el => {
      ["top-left", "top-right", "bottom-left", "bottom-right"].forEach(pos => {
        const corner = document.createElement("div");
        const [v, h] = pos.split("-");
        corner.style.cssText = `
          position:absolute;${v}:8px;${h}:8px;
          width:12px;height:12px;
          border-${v}:1px solid var(--cyan);
          border-${h}:1px solid var(--cyan);
          pointer-events:none;z-index:2;
          opacity:0.6;
        `;
        el.appendChild(corner);
      });
    });
  }

  /* ─────────────────────────────────────────────
     14. ADMIN SIDEBAR TOGGLE
  ───────────────────────────────────────────── */
  function initAdminSidebar() {
    const toggle  = document.getElementById("sidebarToggle");
    const sidebar = document.getElementById("adminSidebar");
    const overlay = document.getElementById("adminOverlay");
    if (!toggle || !sidebar) return;

    toggle.addEventListener("click", () => {
      const open = sidebar.classList.toggle("open");
      if (overlay) overlay.classList.toggle("show", open);
    });
    if (overlay) {
      overlay.addEventListener("click", () => {
        sidebar.classList.remove("open");
        overlay.classList.remove("show");
      });
    }
  }

  /* ─────────────────────────────────────────────
     15. TOAST AUTO-DISMISS
  ───────────────────────────────────────────── */
  function initToasts() {
    document.querySelectorAll(".toast").forEach((toast, i) => {
      setTimeout(() => {
        toast.classList.add("toast--hide");
        setTimeout(() => toast.remove(), 350);
      }, 4200 + i * 300);
    });
  }

  /* ─────────────────────────────────────────────
     16. TABLE SEARCH
  ───────────────────────────────────────────── */
  function initTableSearch() {
    document.querySelectorAll("[data-table-search]").forEach(input => {
      const table = document.getElementById(input.dataset.tableSearch);
      if (!table) return;
      input.addEventListener("input", () => {
        const q = input.value.toLowerCase();
        table.querySelectorAll("tbody tr").forEach(row => {
          row.style.display = row.textContent.toLowerCase().includes(q) ? "" : "none";
        });
      });
    });
    // Generic search (no data attr)
    ["tableSearch", "logSearch"].forEach(id => {
      const el = document.getElementById(id);
      if (!el) return;
      el.addEventListener("input", () => {
        const q = el.value.toLowerCase();
        const tbl = el.closest(".dash__card")?.querySelector("table tbody");
        if (tbl) tbl.querySelectorAll("tr").forEach(r => r.style.display = r.textContent.toLowerCase().includes(q) ? "" : "none");
      });
    });
  }

  /* ─────────────────────────────────────────────
     17. LIVE COLOR PREVIEW (settings)
  ───────────────────────────────────────────── */
  function initColorPreview() {
    const accent  = document.querySelector('input[name="accent_color"]');
    const primary = document.querySelector('input[name="primary_color"]');
    if (accent)  accent.addEventListener("input",  () => document.documentElement.style.setProperty("--plasma", accent.value));
    if (primary) primary.addEventListener("input", () => document.documentElement.style.setProperty("--void",  primary.value));
  }

  /* ─────────────────────────────────────────────
     18. FILE INPUT PREVIEW
  ───────────────────────────────────────────── */
  function initFilePreviews() {
    document.querySelectorAll('input[type="file"][data-preview]').forEach(input => {
      const preview = document.getElementById(input.dataset.preview);
      if (!preview) return;
      input.addEventListener("change", () => {
        const file = input.files[0];
        if (file && file.type.startsWith("image/")) {
          const reader = new FileReader();
          reader.onload = e => { preview.src = e.target.result; preview.style.display = "block"; };
          reader.readAsDataURL(file);
        }
      });
    });
  }

  /* ─────────────────────────────────────────────
     19. PASSWORD TOGGLE
  ───────────────────────────────────────────── */
  window.togglePw = function () {
    const inp = document.getElementById("passwordInput");
    const ico = document.getElementById("pwIcon");
    if (!inp) return;
    const isText = inp.type === "text";
    inp.type = isText ? "password" : "text";
    ico.className = isText ? "fas fa-eye" : "fas fa-eye-slash";
  };

  /* ─────────────────────────────────────────────
     20. PROGRESS BAR on page load
  ───────────────────────────────────────────── */
  function initProgressBar() {
    const bar = document.createElement("div");
    bar.style.cssText = `
      position:fixed;top:0;left:0;height:2px;z-index:99999;
      background:linear-gradient(90deg,var(--violet),var(--plasma),var(--cyan));
      box-shadow:0 0 8px var(--plasma);
      width:0%;transition:width .3s ease;pointer-events:none;
    `;
    document.body.appendChild(bar);

    window.addEventListener("scroll", () => {
      const scrolled = (window.scrollY / (document.documentElement.scrollHeight - window.innerHeight)) * 100;
      bar.style.width = Math.min(scrolled, 100) + "%";
    }, { passive: true });
  }

  /* ─────────────────────────────────────────────
     21. CARD HOVER GLOW TRAIL
  ───────────────────────────────────────────── */
  function initCardGlow() {
    document.querySelectorAll(".skill-card, .edu-card, .cert-card, .timeline__card").forEach(card => {
      card.addEventListener("mousemove", e => {
        const rect = card.getBoundingClientRect();
        const x = ((e.clientX - rect.left) / rect.width)  * 100;
        const y = ((e.clientY - rect.top)  / rect.height) * 100;
        card.style.background = `radial-gradient(circle at ${x}% ${y}%, rgba(139,92,246,0.07), rgba(255,255,255,0.02) 60%)`;
      });
      card.addEventListener("mouseleave", () => {
        card.style.background = "";
      });
    });
  }

  /* ─────────────────────────────────────────────
     22. TIMELINE CONNECTOR ANIMATION
  ───────────────────────────────────────────── */
  function initTimeline() {
    document.querySelectorAll(".timeline__item").forEach((item, i) => {
      const obs = new IntersectionObserver(entries => {
        if (entries[0].isIntersecting) {
          setTimeout(() => {
            item.style.opacity = "1";
            item.style.transform = "translateX(0)";
          }, i * 120);
          obs.unobserve(item);
        }
      }, { threshold: 0.1 });
      item.style.cssText += "opacity:0;transform:translateX(-20px);transition:opacity .6s ease,transform .6s ease;";
      obs.observe(item);
    });
  }

  /* ─────────────────────────────────────────────
     BOOT — Run everything
  ───────────────────────────────────────────── */
  function boot() {
    initProgressBar();
    initNav();
    initMobileNav();
    initSmoothScroll();
    initReveal();
    initCounters();
    initSkills();
    initTimeline();
    initAdminSidebar();
    initToasts();
    initTableSearch();
    initColorPreview();
    initFilePreviews();
    initCursorGlow();
    initHUDDecorations();
    initCardGlow();

    // Slightly delayed for DOM paint
    setTimeout(() => {
      initParticles();
      initTypewriter();
      initGlitch();
      initTiltCards();
      initMagneticButtons();
    }, 300);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }

})();

/* ─────────────────────────────────────────────
   23. FLOATING TECH ICONS — mouse parallax
───────────────────────────────────────────── */
(function initFloatingIcons() {
  const ficons = document.querySelectorAll(".ficon");
  if (!ficons.length) return;

  // Parallax on mouse move inside hero
  const hero = document.querySelector(".hero");
  if (!hero) return;

  hero.addEventListener("mousemove", e => {
    const rect = hero.getBoundingClientRect();
    const cx   = rect.width  / 2;
    const cy   = rect.height / 2;
    const dx   = (e.clientX - rect.left  - cx) / cx;  // -1 to 1
    const dy   = (e.clientY - rect.top   - cy) / cy;

    ficons.forEach((icon, i) => {
      const depth  = .5 + (i % 5) * .3; // different depth per icon
      const tx     = dx * depth * 18;
      const ty     = dy * depth * 14;
      icon.style.setProperty("--px", tx + "px");
      icon.style.setProperty("--py", ty + "px");
      // Apply only the parallax part on top of the float animation
      // We shift the transform-origin gently
      icon.style.marginLeft = tx * .5 + "px";
      icon.style.marginTop  = ty * .5 + "px";
    });
  });

  hero.addEventListener("mouseleave", () => {
    ficons.forEach(icon => {
      icon.style.marginLeft = "0";
      icon.style.marginTop  = "0";
    });
  });

  // Hover glow effect on individual icons
  ficons.forEach(icon => {
    icon.addEventListener("mouseenter", () => {
      icon.style.filter = "drop-shadow(0 0 16px var(--color)) brightness(1.3)";
      icon.style.zIndex = "5";
    });
    icon.addEventListener("mouseleave", () => {
      icon.style.filter = "drop-shadow(0 0 8px var(--color))";
      icon.style.zIndex = "";
    });
  });
})();
