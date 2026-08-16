(function () {
  'use strict';

  var posts = window.blogPosts || [];

  function escapeHtml(value) {
    return String(value).replace(/[&<>'"]/g, function (character) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' }[character];
    });
  }

  function postUrl(post) {
    return 'blog/' + encodeURIComponent(post.slug) + '/';
  }

  function siteUrl(path) {
    var marker = '/blog/';
    var markerIndex = window.location.pathname.indexOf(marker);
    var base = markerIndex === -1 ? window.location.pathname.replace(/[^/]*$/, '') : window.location.pathname.slice(0, markerIndex + 1);
    return base + path.replace(/^\//, '');
  }

  function renderListing() {
    var featuredMount = document.querySelector('[data-featured-post]');
    var grid = document.querySelector('#article-grid');
    if (!featuredMount || !grid) return;

    var featured = posts.find(function (post) { return post.featured; }) || posts[0];
    if (featured) {
      var featuredUrl = postUrl(featured);
      featuredMount.innerHTML =
        '<article class="featured-post">' +
          '<a class="featured-post-image" href="' + featuredUrl + '" aria-label="Read ' + escapeHtml(featured.title) + '">' +
            '<img src="' + escapeHtml(featured.image) + '" alt="' + escapeHtml(featured.imageAlt) + '" loading="eager">' +
          '</a>' +
          '<div class="featured-post-content">' +
            '<div class="post-meta"><span>' + escapeHtml(featured.category) + '</span><time datetime="' + featured.dateTime + '">' + escapeHtml(featured.date) + '</time></div>' +
            '<h3><a href="' + featuredUrl + '">' + escapeHtml(featured.title) + '</a></h3>' +
            '<p>' + escapeHtml(featured.excerpt) + '</p>' +
            '<a class="read-link" href="' + featuredUrl + '">Read article <i class="fas fa-arrow-right" aria-hidden="true"></i></a>' +
          '</div>' +
        '</article>';
    }

    grid.innerHTML = posts.filter(function (post) { return !post.featured; }).map(function (post) {
      var url = postUrl(post);
      var searchText = [post.title, post.category, post.excerpt].concat(post.categories).join(' ').toLowerCase();
      return '<article class="article-card" data-blog-card data-category="' + escapeHtml(post.categories.join(' ')) + '" data-search="' + escapeHtml(searchText) + '">' +
        '<a class="article-image" href="' + url + '" aria-label="Read ' + escapeHtml(post.title) + '"><img src="' + escapeHtml(post.image) + '" alt="' + escapeHtml(post.imageAlt) + '" loading="lazy"></a>' +
        '<div class="article-content"><div class="post-meta"><span>' + escapeHtml(post.category) + '</span><time datetime="' + post.dateTime + '">' + escapeHtml(post.date) + '</time></div>' +
        '<h3><a href="' + url + '">' + escapeHtml(post.title) + '</a></h3><p>' + escapeHtml(post.excerpt) + '</p>' +
        '<a class="read-link" href="' + url + '">Read article <i class="fas fa-arrow-right" aria-hidden="true"></i></a></div></article>';
    }).join('');

    initialiseFilters();
  }

  function renderContentBlock(block) {
    if (block.type === 'lead') return '<p class="article-lead">' + escapeHtml(block.text) + '</p>';
    if (block.type === 'heading') return '<h2>' + escapeHtml(block.text) + '</h2>';
    if (block.type === 'subheading') return '<h3>' + escapeHtml(block.text) + '</h3>';
    if (block.type === 'paragraph') return '<p>' + escapeHtml(block.text) + '</p>';
    if (block.type === 'quote') return '<blockquote>' + escapeHtml(block.text) + '</blockquote>';
    if (block.type === 'code') return '<div class="code-block"><div class="code-toolbar"><span>' + escapeHtml(block.language || 'code') + '</span><button type="button" data-copy-code>Copy</button></div><pre><code>' + escapeHtml(block.text) + '</code></pre></div>';
    if (block.type === 'list' || block.type === 'ordered-list') {
      var tag = block.type === 'ordered-list' ? 'ol' : 'ul';
      return '<' + tag + '>' + block.items.map(function (item) { return '<li>' + escapeHtml(item) + '</li>'; }).join('') + '</' + tag + '>';
    }
    return '';
  }

  function slugFromPath() {
    var parts = window.location.pathname.replace(/\/+$/, '').split('/');
    return decodeURIComponent(parts[parts.length - 1] || '');
  }

  function renderArticle() {
    var mount = document.querySelector('[data-blog-post]');
    if (!mount) return;

    var slug = document.body.dataset.blogSlug || slugFromPath();
    var post = posts.find(function (item) { return item.slug === slug; });
    window.scrollTo(0, 0);

    if (!post) {
      document.title = 'Article Not Found | Omobayonle Ogundele';
      mount.innerHTML = '<section class="article-not-found" role="status"><h1>Article not found</h1><p>The article you\'re looking for doesn\'t exist.</p><a class="read-link" href="' + siteUrl('blog.html') + '"><i class="fas fa-arrow-left" aria-hidden="true"></i> Back to Blog</a></section>';
      return;
    }

    document.title = post.title + ' | Omobayonle Ogundele';
    var description = document.querySelector('meta[name="description"]');
    if (description) description.setAttribute('content', post.introduction);

    mount.innerHTML = '<article class="article-shell">' +
      '<a class="back-to-blog" href="' + siteUrl('blog.html') + '"><i class="fas fa-arrow-left" aria-hidden="true"></i> All articles</a>' +
      '<header class="article-header"><p class="article-eyebrow"><span>Writing</span> / ' + escapeHtml(post.category) + '</p>' +
      '<h1>' + escapeHtml(post.title) + '</h1><p class="article-deck">' + escapeHtml(post.introduction) + '</p>' +
      '<div class="article-byline"><time datetime="' + post.dateTime + '">' + escapeHtml(post.date) + '</time><span>' + escapeHtml(post.readTime) + '</span></div></header>' +
      '<figure class="article-cover"><img src="' + escapeHtml(post.image) + '" alt="' + escapeHtml(post.imageAlt) + '"></figure>' +
      '<div class="article-body">' + post.content.map(renderContentBlock).join('') +
      '<div class="article-footer-links"><a href="' + siteUrl('blog.html') + '"><i class="fas fa-arrow-left" aria-hidden="true"></i> Back to all articles</a><a href="' + siteUrl('index.html#contact') + '">Discuss this article <i class="fas fa-arrow-right" aria-hidden="true"></i></a></div></div></article>';

    initialiseCopyButtons();
  }

  function initialiseFilters() {
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
        var visible = (activeFilter === 'all' || categories.indexOf(activeFilter) !== -1) && (!query || searchableText.indexOf(query) !== -1);
        card.classList.toggle('is-hidden', !visible);
        if (visible) visibleCount += 1;
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
  }

  function initialiseCopyButtons() {
    document.querySelectorAll('[data-copy-code]').forEach(function (button) {
      button.addEventListener('click', function () {
        var code = button.closest('.code-block').querySelector('code').textContent;
        if (!navigator.clipboard) return;
        navigator.clipboard.writeText(code).then(function () {
          button.textContent = 'Copied';
          window.setTimeout(function () { button.textContent = 'Copy'; }, 1400);
        });
      });
    });
  }

  renderListing();
  renderArticle();
}());
