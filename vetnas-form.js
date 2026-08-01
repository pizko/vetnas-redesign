/* vetnas feedback form -> send.php (email + Strapi). Fallback: Strapi directly (staging without PHP). */
(function () {
  'use strict';
  var PHP = 'send.php'; // relative — beget prod handles email + Strapi storage
  var STRAPI = 'https://deltamoscow.ru/cms/api/bookings';
  document.querySelectorAll('form[data-feedback-form]').forEach(function (form) {
    var note = form.querySelector('[data-form-note]');
    var say = function (m, ok) { if (note) { note.textContent = m; note.className = 'vns-form-note ' + (ok ? 'ok' : 'err'); } };
    form.addEventListener('submit', async function (e) {
      e.preventDefault();
      if (form.website && form.website.value) return; // honeypot
      var name = (form.name && form.name.value || '').trim();
      var phone = (form.phone && form.phone.value || '').trim();
      var msg = (form.message && form.message.value || '').trim();
      if (!name || !phone) { say('Укажите имя и телефон.', false); return; }
      if (form.consent && !form.consent.checked) { say('Подтвердите согласие на обработку данных.', false); return; }
      var btn = form.querySelector('[type=submit]'); var old = btn ? btn.textContent : '';
      if (btn) { btn.disabled = true; btn.textContent = 'Отправляем…'; }
      var okDone = false;
      try {
        var res = await fetch(PHP, { method: 'POST', headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ name: name, phone: phone, message: msg, website: '' }) });
        if (res.ok) okDone = true;
      } catch (e1) {}
      if (!okDone) { // fallback: store in Strapi directly (e.g. staging without PHP)
        try {
          var r2 = await fetch(STRAPI, { method: 'POST', headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ data: { site: 'vetnas', name: name, phone: phone, comment: msg, consent: true, source: 'site-form', status: 'new' } }) });
          if (r2.ok) okDone = true;
        } catch (e2) {}
      }
      if (btn) { btn.disabled = false; btn.textContent = old; }
      if (okDone) { form.reset(); say('Спасибо! Заявка отправлена — перезвоним в рабочее время.', true); }
      else { say('Не удалось отправить. Позвоните: +7 (495) 144-48-03', false); }
    });
  });
})();
