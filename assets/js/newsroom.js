(function () {
  'use strict';

  var newsroom = document.querySelector('[data-newsroom]');
  if (!newsroom) return;

  var filters = newsroom.querySelectorAll('[data-newsroom-filters]');
  var links = Array.from(newsroom.querySelectorAll('[data-newsroom-topic]'));
  var topics = new Map(links.map(function (link) {
    return [link.dataset.newsroomTopic, link.textContent];
  }));
  var front = newsroom.querySelectorAll('[data-newsroom-front]');
  var rows = newsroom.querySelectorAll('[data-story-topics]');
  var academy = newsroom.querySelector('[data-newsroom-academy]');
  var heading = newsroom.querySelector('[data-newsroom-heading]');
  var status = newsroom.querySelector('[data-newsroom-status]');

  function render() {
    var requested = new URLSearchParams(window.location.search).get('topic');
    var topic = topics.has(requested) ? requested : '';
    var count = 0;

    front.forEach(function (section) { section.hidden = Boolean(topic); });
    rows.forEach(function (row) {
      row.hidden = topic
        ? !row.dataset.storyTopics.split(' ').includes(topic)
        : row.hasAttribute('data-newsroom-archived');
      if (!row.hidden) count++;
    });
    links.forEach(function (link) {
      if (link.dataset.newsroomTopic === topic) link.setAttribute('aria-current', 'true');
      else link.removeAttribute('aria-current');
    });
    if (academy) {
      var guidesShown = 0;
      academy.querySelectorAll('[data-guide-topics]').forEach(function (guide) {
        var matches = !topic || guide.dataset.guideTopics.split(' ').includes(topic);
        guide.hidden = !matches || guidesShown >= 2;
        if (!guide.hidden) guidesShown++;
      });
      academy.hidden = guidesShown === 0;
    }

    heading.textContent = topic ? topics.get(topic) : 'Latest News';
    status.textContent = topic ? count + (count === 1 ? ' story' : ' stories') + ' about ' + topics.get(topic) : '';
  }

  filters.forEach(function (filter) { filter.hidden = false; });
  newsroom.addEventListener('click', function (event) {
    var link = event.target.closest('[data-newsroom-topic]');
    if (!link || event.defaultPrevented || event.button !== 0 ||
        event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;

    event.preventDefault();
    var url = new URL(window.location.href);
    var topic = link.dataset.newsroomTopic;
    if (topic) url.searchParams.set('topic', topic);
    else url.searchParams.delete('topic');
    if (url.href !== window.location.href) window.history.pushState(null, '', url);
    render();
    if (link.closest('.newsroom-sidebar')) heading.focus();
  });

  window.addEventListener('popstate', render);
  render();
}());
