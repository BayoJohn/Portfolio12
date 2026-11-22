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
