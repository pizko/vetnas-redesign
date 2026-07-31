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

  /* The exported news pagination writes the selected page as plain text.
     Turn it into a real, styled current-page control on every news page. */
  document.querySelectorAll(".g-pagination").forEach(function (pagination) {
    Array.prototype.slice.call(pagination.childNodes).forEach(function (node) {
      if (node.nodeType !== 3) return;

      var pageNumber = node.textContent.trim();
      if (!/^\d+$/.test(pageNumber)) return;

      var current = document.createElement("span");
      current.className = "g-pagination__item g-pagination__item--active";
      current.setAttribute("aria-current", "page");
      current.textContent = pageNumber;
      pagination.replaceChild(current, node);
    });
  });
})();
