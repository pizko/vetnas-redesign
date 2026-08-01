/* vetnas feedback form -> Strapi bookings */
(function () {
  'use strict';
  var API = 'https://deltamoscow.ru/cms/api/bookings', SITE = 'vetnas';
  var forms = document.querySelectorAll('form[data-feedback-form]');
  forms.forEach(function (form) {
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
      try {
        var res = await fetch(API, { method: 'POST', headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ data: { site: SITE, name: name, phone: phone, comment: msg, consent: true, source: 'site-form', status: 'new' } }) });
        if (!res.ok) throw new Error('bad');
        form.reset(); say('Спасибо! Заявка отправлена — перезвоним в рабочее время.', true);
      } catch (err) { say('Не удалось отправить. Позвоните: +7 (495) 144-48-03', false); }
      finally { if (btn) { btn.disabled = false; btn.textContent = old; } }
    });
  });
})();
