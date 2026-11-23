(function () {
  'use strict';

  var copyButton = document.querySelector('[data-copy-article]');
  if (copyButton && navigator.clipboard) {
    var status = document.querySelector('[data-share-status]');
    copyButton.hidden = false;
    copyButton.addEventListener('click', async function () {
      try {
        await navigator.clipboard.writeText(copyButton.dataset.copyArticle);
        status.textContent = 'Article link copied.';
      } catch (error) {
        status.textContent = 'Copy failed. You can copy the URL from the address bar.';
      }
    });
  }

  document.querySelectorAll('.reading-article .article-body pre').forEach(function (block) {
    block.tabIndex = 0;
  });

  var contents = document.querySelector('.reading-toc details');
  if (!contents) return;

  var desktop = window.matchMedia('(min-width: 1060px)');
  function syncContents() {
    contents.open = desktop.matches;
  }
  syncContents();
  desktop.addEventListener('change', syncContents);

  var sections = Array.from(contents.querySelectorAll('a')).map(function (link) {
    var heading = document.getElementById(decodeURIComponent(link.hash.slice(1)));
    return { link: link, heading: heading };
  }).filter(function (section) { return section.heading; });

  sections.forEach(function (section) {
    section.link.addEventListener('click', function () {
      if (!desktop.matches) contents.open = false;
      section.heading.tabIndex = -1;
      section.heading.focus({ preventScroll: true });
    });
  });

  var active;
  var scheduled = false;
  function highlightSection() {
    scheduled = false;
    var offset = document.querySelector('.editorial-nav').getBoundingClientRect().bottom + 36;
    var current = sections.filter(function (section) {
      return section.heading.getBoundingClientRect().top <= offset;
    }).pop();
    if (current === active) return;
    if (active) active.link.removeAttribute('aria-current');
    if (current) current.link.setAttribute('aria-current', 'location');
    active = current;
  }

  function queueHighlight() {
    if (scheduled) return;
    scheduled = true;
    window.requestAnimationFrame(highlightSection);
  }

  window.addEventListener('scroll', queueHighlight, { passive: true });
  window.addEventListener('resize', queueHighlight);
  window.addEventListener('load', queueHighlight);
  queueHighlight();
}());
