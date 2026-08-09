(function () {
  'use strict';

  var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var toggle = document.querySelector('.sidebar-toggle');
  var sidebar = document.querySelector('.profile-sidebar');
  var navLinks = Array.prototype.slice.call(document.querySelectorAll('.sidebar-nav a[href^="#"]'));

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

  var slides = Array.prototype.slice.call(document.querySelectorAll('.hero-slide'));
  var slideIndex = 0;
  var slideTimer;

  function showSlide(nextIndex) {
    if (!slides.length) return;
    slideIndex = (nextIndex + slides.length) % slides.length;
    slides.forEach(function (slide, index) {
      slide.classList.toggle('active', index === slideIndex);
      slide.setAttribute('aria-hidden', String(index !== slideIndex));
    });
  }

  function startSlides() {
    if (reduceMotion || slides.length < 2) return;
    window.clearInterval(slideTimer);
    slideTimer = window.setInterval(function () { showSlide(slideIndex + 1); }, 6000);
  }

  document.querySelectorAll('.hero-controls button').forEach(function (button) {
    button.addEventListener('click', function () {
      showSlide(slideIndex + (button.dataset.direction === 'next' ? 1 : -1));
      startSlides();
    });
  });
  showSlide(0);
  startSlides();

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
