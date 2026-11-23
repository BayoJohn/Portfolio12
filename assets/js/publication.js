(function () {
  'use strict';

  var menu = document.querySelector('.publication-menu');
  var navigation = document.getElementById('site-navigation');
  var mobile = window.matchMedia('(max-width: 900px)');

  function setMenu(open) {
    menu.setAttribute('aria-expanded', String(open));
    navigation.hidden = mobile.matches && !open;
  }

  if (menu && navigation) {
    menu.hidden = false;
    setMenu(false);
    menu.addEventListener('click', function () {
      var open = menu.getAttribute('aria-expanded') !== 'true';
      setMenu(open);
      if (open) navigation.querySelector('a').focus();
    });
    menu.closest('header').addEventListener('keydown', function (event) {
      if (event.key === 'Escape' && menu.getAttribute('aria-expanded') === 'true') {
        setMenu(false);
        menu.focus();
      }
    });
    mobile.addEventListener('change', function () { setMenu(false); });
  }

  var carousel = document.querySelector('.publication-carousel');
  if (carousel) setupCarousel(carousel);

  function setupCarousel(carousel) {
    var stage = carousel.querySelector('.carousel-stage');
    var slides = Array.from(stage.querySelectorAll('.carousel-slide'));
    var controls = stage.querySelector('.carousel-controls');
    var counter = controls.querySelector('.carousel-count');
    var status = stage.querySelector('.carousel-status');
    var thumbnailRow = carousel.querySelector('.carousel-thumbnails');
    var thumbnails = Array.from(thumbnailRow.querySelectorAll('button'));
    var index = 0;
    var touchStart;
    var swipeTime = -Infinity;

    function show(next) {
      next = (next + slides.length) % slides.length;
      if (next === index) return;

      var previous = slides[index];
      var active = slides[next];
      var photo = active.querySelector('.carousel-photo');
      if (photo.dataset.srcset) {
        photo.srcset = photo.dataset.srcset;
        delete photo.dataset.srcset;
      }

      thumbnails[index].removeAttribute('aria-current');
      thumbnails[next].setAttribute('aria-current', 'true');
      if (previous.contains(document.activeElement)) {
        thumbnails[next].focus({preventScroll: true});
      }
      previous.classList.remove('is-active');
      previous.inert = true;
      previous.setAttribute('aria-hidden', 'true');
      active.classList.add('is-active');
      active.inert = false;
      active.removeAttribute('aria-hidden');
      index = next;

      var current = index + 1;
      counter.textContent = String(current).padStart(2, '0') + ' / ' + String(slides.length).padStart(2, '0');
      status.textContent = thumbnails[index].dataset.label + ', slide ' + current + ' of ' + slides.length;
      var bounds = thumbnails[index].getBoundingClientRect();
      var rowBounds = thumbnailRow.getBoundingClientRect();
      if (bounds.left < rowBounds.left || bounds.right > rowBounds.right) {
        thumbnailRow.scrollLeft += bounds.left - rowBounds.left - 4;
      }
    }

    controls.querySelectorAll('button').forEach(function (button) {
      button.addEventListener('click', function () { show(index + Number(button.dataset.step)); });
    });
    thumbnails.forEach(function (button, target) {
      button.addEventListener('click', function () { show(target); });
    });
    carousel.addEventListener('keydown', function (event) {
      if (event.key !== 'ArrowLeft' && event.key !== 'ArrowRight') return;
      if (event.altKey || event.ctrlKey || event.metaKey || event.shiftKey) return;
      event.preventDefault();
      show(index + (event.key === 'ArrowLeft' ? -1 : 1));
      if (thumbnailRow.contains(event.target)) thumbnails[index].focus({preventScroll: true});
    });

    stage.addEventListener('pointerdown', function (event) {
      if (event.pointerType === 'touch' && event.isPrimary && !event.target.closest('button')) {
        touchStart = {id: event.pointerId, x: event.clientX, y: event.clientY};
      }
    });
    stage.addEventListener('pointercancel', function () { touchStart = null; });
    stage.addEventListener('pointerup', function (event) {
      if (!touchStart || touchStart.id !== event.pointerId) return;
      var horizontal = event.clientX - touchStart.x;
      var vertical = event.clientY - touchStart.y;
      touchStart = null;
      if (Math.abs(horizontal) > 45 && Math.abs(horizontal) > Math.abs(vertical) * 1.35) {
        swipeTime = event.timeStamp;
        show(index + (horizontal < 0 ? 1 : -1));
      }
    });
    stage.addEventListener('click', function (event) {
      if (event.detail > 0 && event.timeStamp - swipeTime < 400 && event.target.closest('a')) {
        event.preventDefault();
      }
    }, true);

    controls.hidden = false;
    thumbnailRow.hidden = false;
  }

  if (!navigator.clipboard) return;

  document.querySelectorAll('.article-body pre > code').forEach(function (code) {
    var block = document.createElement('div');
    block.className = 'code-block';
    var toolbar = document.createElement('div');
    toolbar.className = 'code-toolbar';
    var button = document.createElement('button');
    button.type = 'button';
    button.textContent = 'Copy code';
    var status = document.createElement('output');
    var timer;
    button.addEventListener('click', function () {
      navigator.clipboard.writeText(code.textContent).then(function () {
        status.textContent = 'Copied';
      }, function () {
        status.textContent = 'Could not copy';
      }).finally(function () {
        clearTimeout(timer);
        timer = setTimeout(function () { status.textContent = ''; }, 2500);
      });
    });
    toolbar.append(button, status);
    code.parentElement.before(block);
    block.append(toolbar, code.parentElement);
  });
}());
