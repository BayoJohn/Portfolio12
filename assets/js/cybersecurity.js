(function () {
  'use strict';

  const scope = document.querySelector('[data-vulnerability-table]');
  if (!scope || !scope.querySelector("form")) return;

  const controls = scope.querySelector('form');
  const rows = Array.from(scope.querySelectorAll('tbody tr'));
  const status = scope.querySelector('[role="status"]');

  function filter() {
    const selected = Array.from(controls.querySelectorAll('select'));
    let count = 0;
    for (const row of rows) {
      const match = selected.every(select => !select.value || select.value === row.dataset[select.name]);
      row.hidden = !match;
      if (match) count++;
    }
    status.textContent = count ? 'Showing ' + count + ' of ' + rows.length + ' vulnerabilities.' : 'No vulnerabilities match these filters.';
  }

  controls.hidden = false;
  controls.addEventListener('change', filter);
  controls.addEventListener('submit', event => event.preventDefault());
  controls.addEventListener('reset', () => window.setTimeout(filter, 0));
  window.addEventListener('hashchange', () => {
    const target = rows.find(row => '#' + row.id === location.hash);
    if (target && target.hidden) {
      controls.reset();
      filter();
      target.focus();
    }
  });
  filter();
}());
