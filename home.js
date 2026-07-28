/* Homepage reviews slider — shows 1 (mobile) or 2 (desktop) reviews, auto-rotates. */
(function () {
  'use strict';
  function init(root) {
    var track = root.querySelector('.reviews-track');
    var slides = Array.prototype.slice.call(root.querySelectorAll('.concept-review'));
    var prev = root.querySelector('.reviews-prev');
    var next = root.querySelector('.reviews-next');
    var dotsWrap = root.querySelector('.reviews-dots');
    if (!track || slides.length === 0) return;

    var index = 0;
    var timer = null;

    function perView() { return window.matchMedia('(min-width: 768px)').matches ? 2 : 1; }
    function pages() { return Math.max(1, Math.ceil(slides.length / perView())); }

    function buildDots() {
      if (!dotsWrap) return;
      dotsWrap.innerHTML = '';
      for (var i = 0; i < pages(); i++) {
        var b = document.createElement('button');
        b.type = 'button';
        b.className = 'reviews-dot' + (i === index ? ' active' : '');
        b.setAttribute('aria-label', 'Отзывы, страница ' + (i + 1));
        (function (p) { b.addEventListener('click', function () { go(p); restart(); }); })(i);
        dotsWrap.appendChild(b);
      }
    }
    function render() {
      var pv = perView();
      var offset = -(index * 100);
      track.style.transform = 'translateX(' + offset + '%)';
      slides.forEach(function (s) { s.style.flex = '0 0 ' + (100 / pv) + '%'; s.style.maxWidth = (100 / pv) + '%'; });
      if (dotsWrap) {
        var dots = dotsWrap.querySelectorAll('.reviews-dot');
        dots.forEach(function (d, i) { d.classList.toggle('active', i === index); });
      }
    }
    function go(p) { index = (p + pages()) % pages(); render(); }
    function nextPage() { go(index + 1); }
    function prevPage() { go(index - 1); }
    function restart() { if (timer) clearInterval(timer); timer = setInterval(nextPage, 5000); }

    if (next) next.addEventListener('click', function () { nextPage(); restart(); });
    if (prev) prev.addEventListener('click', function () { prevPage(); restart(); });
    window.addEventListener('resize', function () { if (index >= pages()) index = pages() - 1; buildDots(); render(); });
    root.addEventListener('mouseenter', function () { if (timer) clearInterval(timer); });
    root.addEventListener('mouseleave', restart);

    buildDots();
    render();
    restart();
  }

  function boot() {
    document.querySelectorAll('[data-reviews-slider]').forEach(init);
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot);
  else boot();
})();
