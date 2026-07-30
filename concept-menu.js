(function () {
  var paletteStylesheet = document.querySelector('link[href*="palais-vet.css"]');

  if (paletteStylesheet && !paletteStylesheet.href.includes('v=20260730-menu-overlay')) {
    paletteStylesheet.href += (paletteStylesheet.href.includes('?') ? '&' : '?') + 'v=20260730-menu-overlay';
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
