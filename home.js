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

/* Gallery lightbox — click a photo to open it full-size. */
(function () {
  'use strict';
  var box = document.querySelector('[data-lightbox]');
  if (!box) return;
  var img = box.querySelector('img');
  var close = box.querySelector('.vns-lightbox__close');
  function open(src, alt) { img.src = src; img.alt = alt || ''; box.classList.add('open'); box.setAttribute('aria-hidden', 'false'); }
  function hide() { box.classList.remove('open'); box.setAttribute('aria-hidden', 'true'); img.src = ''; }
  document.querySelectorAll('.concept-gallery img').forEach(function (el) {
    el.style.cursor = 'zoom-in';
    el.addEventListener('click', function () { open(el.getAttribute('src'), el.getAttribute('alt')); });
  });
  box.addEventListener('click', function (e) { if (e.target === box) hide(); });
  if (close) close.addEventListener('click', hide);
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape') hide(); });
})();

/* Consent modal — opened from the form's "пользовательским соглашением" link. */
(function () {
  'use strict';
  var modal = document.querySelector('[data-consent-modal]');
  if (!modal) return;
  function open(e) { if (e) e.preventDefault(); modal.classList.add('open'); modal.setAttribute('aria-hidden', 'false'); }
  function hide() { modal.classList.remove('open'); modal.setAttribute('aria-hidden', 'true'); }
  document.querySelectorAll('[data-consent-open]').forEach(function (a) { a.addEventListener('click', open); });
  var close = modal.querySelector('[data-consent-close]');
  if (close) close.addEventListener('click', hide);
  modal.addEventListener('click', function (e) { if (e.target === modal) hide(); });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape') hide(); });
})();

/* Feedback form -> Strapi booking. */
(function () {
  'use strict';
  var API = 'https://deltamoscow.ru/cms/api/bookings';
  var SITE = 'vetnas';
  var form = document.querySelector('[data-feedback-form]');
  if (!form) return;
  var note = form.querySelector('[data-form-note]');
  function say(msg, ok) { if (note) { note.textContent = msg; note.className = 'vns-form-note' + (ok ? ' is-ok' : ' is-err'); } }

  form.addEventListener('submit', async function (e) {
    e.preventDefault();
    if (form.website.value) return; // honeypot
    var name = form.name.value.trim();
    var phone = form.phone.value.trim();
    var message = form.message.value.trim();
    if (!name || !phone) { say('Укажите имя и телефон.', false); return; }
    if (!form.consent.checked) { say('Подтвердите согласие на обработку данных.', false); return; }
    var btn = form.querySelector('.vns-form-submit');
    btn.disabled = true; btn.textContent = 'Отправляем…';
    try {
      var res = await fetch(API, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ data: { site: SITE, name: name, phone: phone, comment: message, consent: true, source: 'site-form', status: 'new' } })
      });
      if (!res.ok) throw new Error('bad status');
      form.reset();
      say('Спасибо! Заявка отправлена — мы перезвоним.', true);
    } catch (err) {
      say('Не удалось отправить. Позвоните нам: +7 (495) 144-48-03', false);
    } finally {
      btn.disabled = false; btn.textContent = 'Отправить заявку';
    }
  });
})();
