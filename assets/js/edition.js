(function () {
  'use strict';

  const feed = document.querySelector('[data-edition-feed]');
  const more = document.querySelector('[data-edition-more]');
  const status = document.querySelector('[data-edition-status]');
  const stories = Array.from(feed.children);
  const batchSize = 4;
  let shown = batchSize;

  if (stories.length <= batchSize) return;

  stories.slice(shown).forEach(story => { story.hidden = true; });
  more.hidden = false;
  more.addEventListener('click', () => {
    const next = Math.min(shown + batchSize, stories.length);
    stories.slice(shown, next).forEach(story => { story.hidden = false; });
    stories[shown].querySelector('a').focus();
    shown = next;
    more.hidden = shown === stories.length;
    status.textContent = 'Showing ' + shown + ' of ' + stories.length + ' stories.';
  });
}());
