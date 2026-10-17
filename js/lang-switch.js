/* 中 / EN 语言切换按钮（readthedocs 主题没有内置语言选择器） */
(function () {
  function targetUrl() {
    var path = location.pathname;
    var idx = path.indexOf('/en/');
    if (idx >= 0) {
      return path.slice(0, idx) + '/' + path.slice(idx + 4);
    }
    var home = document.querySelector('.wy-side-nav-search > a');
    var base = home ? new URL(home.href).pathname : '/';
    if (path.indexOf(base) === 0) {
      return base + 'en/' + path.slice(base.length);
    }
    return 'en/';
  }

  function addToggle() {
    var box = document.querySelector('.wy-side-nav-search');
    if (!box || document.getElementById('lang-switch')) return;
    var isEn = location.pathname.indexOf('/en/') >= 0;
    var a = document.createElement('a');
    a.id = 'lang-switch';
    a.href = targetUrl();
    a.textContent = isEn ? '中文' : 'English';
    a.title = isEn ? '切换到中文帮助' : 'Switch to English help';
    a.style.cssText = [
      'display:inline-block',
      'margin:8px 0 2px',
      'padding:3px 12px',
      'border:1px solid #2980b9',
      'border-radius:12px',
      'color:#2980b9',
      'background:#fff',
      'font-size:12px',
      'line-height:1.6',
      'text-decoration:none'
    ].join(';');
    box.appendChild(a);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', addToggle);
  } else {
    addToggle();
  }
})();
