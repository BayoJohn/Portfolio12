(function () {
  'use strict';

  var search = document.querySelector('#blog-search');
  var filters = Array.prototype.slice.call(document.querySelectorAll('[data-blog-filter]'));
  var cards = Array.prototype.slice.call(document.querySelectorAll('[data-blog-card]'));
  var emptyState = document.querySelector('.blog-empty');
  var activeFilter = 'all';

  function updateArticles() {
    var query = search ? search.value.trim().toLowerCase() : '';
    var visibleCount = 0;

    cards.forEach(function (card) {
      var categories = (card.dataset.category || '').split(' ');
      var searchableText = (card.dataset.search || card.textContent).toLowerCase();
      var categoryMatches = activeFilter === 'all' || categories.indexOf(activeFilter) !== -1;
      var searchMatches = !query || searchableText.indexOf(query) !== -1;
      var isVisible = categoryMatches && searchMatches;
      card.classList.toggle('is-hidden', !isVisible);
      if (isVisible) visibleCount += 1;
    });

    if (emptyState) emptyState.hidden = visibleCount !== 0;
  }

  filters.forEach(function (button) {
    button.addEventListener('click', function () {
      activeFilter = button.dataset.blogFilter;
      filters.forEach(function (item) { item.classList.toggle('active', item === button); });
      updateArticles();
    });
  });

  if (search) search.addEventListener('input', updateArticles);

  document.querySelectorAll('[data-copy-code]').forEach(function (button) {
    button.addEventListener('click', function () {
      var code = button.closest('.code-block').querySelector('code').textContent;
      if (!navigator.clipboard) return;
      navigator.clipboard.writeText(code).then(function () {
        var originalText = button.textContent;
        button.textContent = 'Copied';
        window.setTimeout(function () { button.textContent = originalText; }, 1400);
      });
    });
  });
}());
