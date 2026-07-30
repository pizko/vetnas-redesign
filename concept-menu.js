(function () {
  var paletteStylesheet = document.querySelector('link[href*="palais-vet.css"]');

  if (paletteStylesheet && !paletteStylesheet.href.includes('v=20260730-blob-layer')) {
    paletteStylesheet.href += (paletteStylesheet.href.includes('?') ? '&' : '?') + 'v=20260730-blob-layer';
  }

  var conceptPage = document.querySelector('.concept-page');

  if (conceptPage && !conceptPage.querySelector('.concept-medical-icons')) {
    var medicalIcons = document.createElement('div');
    medicalIcons.className = 'concept-medical-icons';
    medicalIcons.setAttribute('aria-hidden', 'true');

    ['🐾', '🩺', '🐾', '🔬', '🐾', '🐾'].forEach(function (icon) {
      var mark = document.createElement('span');
      mark.textContent = icon;
      medicalIcons.appendChild(mark);
    });

    conceptPage.insertBefore(medicalIcons, conceptPage.firstChild);
  }

  document.addEventListener("click", function (event) {
    document.querySelectorAll(".concept-side-menu[open]").forEach(function (menu) {
      if (!menu.contains(event.target)) {
        menu.removeAttribute("open");
      }
    });
  });

  document.addEventListener("keydown", function (event) {
    if (event.key !== "Escape") {
      return;
    }

    document.querySelectorAll(".concept-side-menu[open]").forEach(function (menu) {
      menu.removeAttribute("open");
    });
  });
})();
