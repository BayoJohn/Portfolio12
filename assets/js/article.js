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

  var codeLanguages = {
    shell: 'Shell',
    bash: 'Bash',
    terminal: 'Shell',
    dockerfile: 'Dockerfile',
    yaml: 'YAML',
    hcl: 'HCL',
    promql: 'PromQL'
  };
  var codeTokens = {
    shell: /"(?:\\.|[^"\\])*"|'[^']*'|(?:^|[ \t])#[^\n]*|\$\{[^}\n]+\}|\$[A-Za-z_]\w*|(?:^|(?<=&&|\|\|))[ \t]*[\w.-]+|(?<![\w./-])--?[\w-]+/gm,
    dockerfile: /"(?:\\.|[^"\\])*"|'[^']*'|^[ \t]*#[^\n]*|^[ \t]*(?:FROM|WORKDIR|COPY|RUN|ENV|USER|EXPOSE|CMD|ENTRYPOINT|ARG|ADD|LABEL|SHELL|HEALTHCHECK|VOLUME|STOPSIGNAL|ONBUILD)\b|\bAS\b/gm,
    yaml: /"(?:\\.|[^"\\])*"|'[^']*'|(?:^|[ \t])#[^\n]*|[\w.-]+(?=:[ \t]|:$)|\b(?:true|false|null|\d+(?:\.\d+)?)\b/gm,
    hcl: /"(?:\\.|[^"\\])*"|'[^']*'|(?:^|[ \t])(?:#|\/\/)[^\n]*|\b(?:module|resource|data|variable|output|locals|provider|terraform|var)\b|\b(?:true|false|null|\d+(?:\.\d+)?)\b/gm,
    promql: /"(?:\\.|[^"\\])*"|'[^']*'|(?:^|[ \t])#[^\n]*|\b\w+(?=\()|\b(?:by|without|on|ignoring|and|or|unless)\b|\b\d+(?:\.\d+)?[smhdwy]?\b/gm
  };

  document.querySelectorAll('.reading-article .article-body pre > code').forEach(function (code) {
    var language = Object.keys(codeLanguages).find(function (name) {
      return code.classList.contains('language-' + name);
    });
    if (!language) return;

    var toolbar = code.closest('.code-block')?.querySelector('.code-toolbar');
    if (toolbar) {
      var label = document.createElement('span');
      label.className = 'code-language';
      label.textContent = codeLanguages[language];
      toolbar.prepend(label);
    }

    var input = code.textContent;
    var tokens = codeTokens[language] || codeTokens.shell;
    var highlighted = document.createDocumentFragment();
    var offset = 0;
    for (var match of input.matchAll(tokens)) {
      highlighted.append(input.slice(offset, match.index));
      var token = document.createElement('span');
      var value = match[0].trimStart();
      var type = 'keyword';
      if (/^(?:#|\/\/)/.test(value)) type = 'comment';
      else if (/^["']/.test(value)) type = 'string';
      else if (/^(?:\$|-|\d|true$|false$|null$)/.test(value)) type = 'value';
      token.className = 'syntax-' + type;
      token.textContent = match[0];
      highlighted.append(token);
      offset = match.index + match[0].length;
    }
    highlighted.append(input.slice(offset));
    code.replaceChildren(highlighted);
  });

  var contents = document.querySelector('.reading-toc details');
  if (!contents) return;

  var sections = Array.from(contents.querySelectorAll('a')).map(function (link) {
    var heading = document.getElementById(decodeURIComponent(link.hash.slice(1)));
    return { link: link, heading: heading };
  }).filter(function (section) { return section.heading; });

  sections.forEach(function (section) {
    section.link.addEventListener('click', function () {
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
