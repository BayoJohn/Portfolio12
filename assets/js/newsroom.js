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

(function () {
  'use strict';

  var section = document.querySelector('[data-external-news]');
  if (!section) return;

  var snapshot = new URL('../data/tech-news.json', document.currentScript.src);
  var list = section.querySelector('[data-external-list]');
  var status = section.querySelector('[data-external-status]');
  var more = section.querySelector('[data-external-more]');
  var batchSize = 8;
  var maxAge = 14 * 24 * 60 * 60 * 1000;
  var publishers = new Map([
    ['Electronic Frontier Foundation', 'eff.org'],
    ['NASA', 'nasa.gov']
  ]);
  var stories = [];
  var shown = 0;
  var formatter = new Intl.DateTimeFormat('en', { dateStyle: 'medium', timeZone: 'UTC' });

  function safeStory(story, oldest) {
    if (!story || !publishers.has(story.publisher) || typeof story.headline !== 'string' ||
        !story.headline || typeof story.category !== 'string' ||
        typeof story.id !== 'string' || !/^[a-f0-9]{64}$/.test(story.id)) return false;
    var age = Date.parse(story.published_at || story.fetched_at);
    if (!Number.isFinite(age) || age < oldest) return false;
    try {
      var url = new URL(story.url);
      var domain = publishers.get(story.publisher);
      return url.protocol === 'https:' && !url.username && !url.password && !url.port &&
        (url.hostname === domain || url.hostname.endsWith('.' + domain));
    } catch (error) {
      return false;
    }
  }

  function textElement(tag, text) {
    var element = document.createElement(tag);
    element.textContent = text;
    return element;
  }

  function appendBatch() {
    var fragment = document.createDocumentFragment();
    var firstLink;
    stories.slice(shown, shown + batchSize).forEach(function (story) {
      var row = document.createElement('li');
      row.className = 'newsroom-external-row';
      var heading = document.createElement('h3');
      var link = textElement('a', story.headline);
      link.href = story.url;
      link.target = '_blank';
      link.rel = 'noopener noreferrer external';
      link.append(textElement('span', ' (opens in a new tab)'));
      link.lastChild.className = 'sr-only';
      heading.append(link);
      if (!firstLink) firstLink = link;

      var metadata = document.createElement('p');
      metadata.className = 'newsroom-meta';
      metadata.append(textElement('span', story.publisher));
      if (story.published_at) {
        var time = textElement('time', formatter.format(new Date(story.published_at)));
        time.dateTime = story.published_at;
        metadata.append(time);
      }
      metadata.append(textElement('span', story.category));
      row.append(heading, metadata);
      if (typeof story.description === 'string' && story.description.trim() && story.description.length <= 200) {
        var description = textElement('p', story.description);
        description.className = 'newsroom-summary';
        row.append(description);
      }
      fragment.append(row);
    });
    list.append(fragment);
    if (shown && firstLink) firstLink.focus();
    shown = Math.min(stories.length, shown + batchSize);
    more.hidden = shown >= stories.length;
    status.textContent = 'Showing ' + shown + ' of ' + stories.length + ' headlines.';
    status.classList.add('sr-only');
  }

  more.addEventListener('click', appendBatch);
  status.textContent = 'Checking for recent headlines…';
  var controller = new AbortController();
  var timeout = window.setTimeout(function () { controller.abort(); }, 5000);
  fetch(snapshot, { signal: controller.signal, credentials: 'same-origin' })
    .then(function (response) {
      if (!response.ok) throw new Error('Snapshot unavailable');
      return response.json();
    })
    .then(function (data) {
      if (!data || data.version !== 1 || !Array.isArray(data.stories)) return;
      var oldest = Date.now() - maxAge;
      var seen = new Set();
      stories = data.stories.slice(0, 48).filter(function (story) {
        if (!safeStory(story, oldest) || seen.has(story.id)) return false;
        seen.add(story.id);
        return true;
      });
      if (stories.length) appendBatch();
    })
    .catch(function () {
      // The original stories and the external headline empty state remain usable.
    })
    .finally(function () {
      window.clearTimeout(timeout);
      if (!shown) status.textContent = 'No recent external headlines are available.';
    });
}());
