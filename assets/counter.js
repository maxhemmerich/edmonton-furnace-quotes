/* Edmonton Furnace Quotes — page-view counter.
   One anonymous page-view beacon per page load, counted by a free third-party service
   (abacus.jasoncameron.dev): no signup, no key, no cookie, no identifier, no personal
   data. It records that a page was opened — nothing about who opened it or what they did.
   The request form is unchanged and still has no server: it composes the request locally
   and hands it to the visitor's mail app. If this beacon fails, the page is unaffected. */
(function () {
  "use strict";

  var NS = "edmonton-furnace-quotes";
  var BASE = "https://abacus.jasoncameron.dev/hit/" + NS + "/";

  var el = document.currentScript;
  var key = (el && el.getAttribute("data-counter")) || "";
  if (!/^[a-z0-9-]+$/.test(key)) { return; }

  function ping() {
    try {
      var img = new Image();
      img.referrerPolicy = "no-referrer";
      img.src = BASE + key + "?_=" + Date.now();
    } catch (e) { /* counted or not, the page does not depend on it */ }
  }

  if (document.readyState === "complete") { ping(); }
  else { window.addEventListener("load", ping, { once: true }); }
})();
