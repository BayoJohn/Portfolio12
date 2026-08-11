(function () {
  'use strict';

  var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var toggle = document.querySelector('.sidebar-toggle');
  var sidebar = document.querySelector('.profile-sidebar');
  var themeToggle = document.querySelector('.theme-toggle');
  var navLinks = Array.prototype.slice.call(document.querySelectorAll('.sidebar-nav a[href^="#"]'));

  function setTheme(theme, persist) {
    var isDark = theme === 'dark';
    document.documentElement.setAttribute('data-theme', isDark ? 'dark' : 'light');
    if (themeToggle) {
      themeToggle.setAttribute('aria-pressed', String(isDark));
      themeToggle.setAttribute('aria-label', isDark ? 'Switch to light mode' : 'Switch to dark mode');
      themeToggle.querySelector('span').textContent = isDark ? 'Light' : 'Dark';
      themeToggle.querySelector('i').className = isDark ? 'fas fa-sun' : 'far fa-moon';
    }
    if (persist) {
      try { localStorage.setItem('theme', isDark ? 'dark' : 'light'); } catch (error) {}
    }
  }

  var initialTheme = document.documentElement.getAttribute('data-theme') === 'dark' ? 'dark' : 'light';
  setTheme(initialTheme, false);

  if (themeToggle) {
    themeToggle.addEventListener('click', function () {
      setTheme(document.documentElement.getAttribute('data-theme') === 'dark' ? 'light' : 'dark', true);
    });
  }

  function closeMenu() {
    if (!toggle || !sidebar) return;
    toggle.classList.remove('open');
    sidebar.classList.remove('open');
    toggle.setAttribute('aria-expanded', 'false');
  }

  if (toggle && sidebar) {
    toggle.addEventListener('click', function () {
      var isOpen = sidebar.classList.toggle('open');
      toggle.classList.toggle('open', isOpen);
      toggle.setAttribute('aria-expanded', String(isOpen));
    });

    document.addEventListener('keydown', function (event) {
      if (event.key === 'Escape') closeMenu();
    });
  }

  navLinks.forEach(function (link) {
    link.addEventListener('click', function (event) {
      var target = document.querySelector(link.getAttribute('href'));
      if (!target) return;
      event.preventDefault();
      target.scrollIntoView({ behavior: reduceMotion ? 'auto' : 'smooth', block: 'start' });
      closeMenu();
    });
  });

  document.querySelectorAll('a[href^="#"]:not(.sidebar-nav a)').forEach(function (link) {
    link.addEventListener('click', function (event) {
      var href = link.getAttribute('href');
      if (!href || href === '#') return;
      var target = document.querySelector(href);
      if (!target) return;
      event.preventDefault();
      target.scrollIntoView({ behavior: reduceMotion ? 'auto' : 'smooth', block: 'start' });
    });
  });

  var sections = document.querySelectorAll('.page-section[id]');
  if ('IntersectionObserver' in window) {
    var sectionObserver = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        navLinks.forEach(function (link) {
          link.classList.toggle('active', link.getAttribute('href') === '#' + entry.target.id);
        });
      });
    }, { rootMargin: '-25% 0px -60% 0px', threshold: 0 });
    sections.forEach(function (section) { sectionObserver.observe(section); });
  }

  var reveals = document.querySelectorAll('.reveal');
  if (reduceMotion || !('IntersectionObserver' in window)) {
    reveals.forEach(function (element) { element.classList.add('visible'); });
  } else {
    var revealObserver = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        entry.target.classList.add('visible');
        revealObserver.unobserve(entry.target);
      });
    }, { threshold: 0.14, rootMargin: '0px 0px -45px' });
    reveals.forEach(function (element) { revealObserver.observe(element); });
  }

  var heroImages = Array.prototype.slice.call(document.querySelectorAll('.hero-carousel-image'));
  var heroImageIndex = 0;
  var heroImageTimer;

  function showHeroImage(nextIndex) {
    if (!heroImages.length) return;
    heroImageIndex = (nextIndex + heroImages.length) % heroImages.length;
    heroImages.forEach(function (image, index) {
      var isActive = index === heroImageIndex;
      image.classList.toggle('active', isActive);
      image.setAttribute('aria-hidden', String(!isActive));
    });
  }

  function stopHeroAutoplay() {
    window.clearInterval(heroImageTimer);
    heroImageTimer = null;
  }

  function startHeroAutoplay() {
    if (reduceMotion || heroImages.length < 2 || heroImageTimer) return;
    heroImageTimer = window.setInterval(function () {
      showHeroImage(heroImageIndex + 1);
    }, 6000);
  }

  document.querySelectorAll('.hero-controls button').forEach(function (button) {
    button.addEventListener('click', function () {
      stopHeroAutoplay();
      showHeroImage(heroImageIndex + (button.dataset.direction === 'next' ? 1 : -1));
    });
  });

  showHeroImage(0);
  startHeroAutoplay();

  var counterBand = document.querySelector('.stats-banner');
  var countersStarted = false;

  function animateCounter(counter) {
    var target = Number(counter.dataset.counter);
    var start = performance.now();
    var duration = 1200;
    function update(now) {
      var progress = Math.min((now - start) / duration, 1);
      counter.textContent = Math.floor(target * (1 - Math.pow(1 - progress, 3))) + '+';
      if (progress < 1) requestAnimationFrame(update);
    }
    requestAnimationFrame(update);
  }

  if (counterBand && 'IntersectionObserver' in window) {
    var counterObserver = new IntersectionObserver(function (entries) {
      if (entries[0].isIntersecting && !countersStarted) {
        countersStarted = true;
        document.querySelectorAll('[data-counter]').forEach(animateCounter);
        counterObserver.disconnect();
      }
    }, { threshold: .3 });
    counterObserver.observe(counterBand);
  }

  document.querySelectorAll('.education-item button').forEach(function (button) {
    button.addEventListener('click', function () {
      var item = button.closest('.education-item');
      var wasOpen = item.classList.contains('open');
      document.querySelectorAll('.education-item').forEach(function (educationItem) {
        educationItem.classList.remove('open');
        educationItem.querySelector('button').setAttribute('aria-expanded', 'false');
      });
      if (!wasOpen) {
        item.classList.add('open');
        button.setAttribute('aria-expanded', 'true');
      }
    });
  });

  var filterButtons = document.querySelectorAll('.project-filter button');
  var projectCards = document.querySelectorAll('.project-card');
  filterButtons.forEach(function (button) {
    button.addEventListener('click', function () {
      filterButtons.forEach(function (item) { item.classList.remove('active'); });
      button.classList.add('active');
      var filter = button.dataset.filter;
      projectCards.forEach(function (card) {
        var categories = card.dataset.category.split(' ');
        card.classList.toggle('hidden', filter !== 'all' && categories.indexOf(filter) === -1);
      });
    });
  });
}());
