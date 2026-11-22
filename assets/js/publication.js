(function () {
  'use strict';

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
