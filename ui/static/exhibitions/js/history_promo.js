/* history.baregorc.com pop-up: the Ararat button opens a card that cycles through four sections
   of the history site (the sky changes from dawn to night). It opens by itself once per visit,
   unless the visitor closed it before or the cookie banner is still waiting for an answer. */
(function () {
  "use strict";
  var KEY = "bx-history-promo";
  var OPEN_AFTER = 9000;
  var NEXT_AFTER = 6500;

  function stored(value) {
    try {
      if (value === undefined) return window.sessionStorage.getItem(KEY);
      window.sessionStorage.setItem(KEY, value);
    } catch (error) { /* private mode: the card just opens again on the next page */ }
    return null;
  }

  function start() {
    var root = document.querySelector("[data-bx-hp]");
    if (!root) return;
    var card = root.querySelector(".bx-hp__card");
    var toggle = root.querySelector("[data-bx-hp-toggle]");
    var go = root.querySelector("[data-bx-hp-go]");
    var slides = Array.prototype.slice.call(root.querySelectorAll("[data-bx-hp-slide]"));
    var dots = Array.prototype.slice.call(root.querySelectorAll("[data-bx-hp-dot]"));
    var calm = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    var current = 0;
    var timer = 0;
    var paused = false;

    function show(index) {
      var before = slides[current];
      current = (index + slides.length) % slides.length;
      var slide = slides[current];
      if (before !== slide) {
        before.hidden = true;
        slide.hidden = false;
        if (!calm) {
          slide.classList.remove("is-entering");
          void slide.offsetWidth;
          slide.classList.add("is-entering");
        }
      }
      dots.forEach(function (dot, i) {
        if (i === current) dot.setAttribute("aria-current", "true");
        else dot.removeAttribute("aria-current");
      });
      root.dataset.sky = slide.dataset.sky;
      go.href = slide.href;
      card.setAttribute("aria-labelledby", slide.querySelector(".bx-hp__title").id || "bx-hp-title-0");
    }

    function tick() {
      clearTimeout(timer);
      if (calm || card.hidden) return;
      timer = setTimeout(function () {
        if (!paused) show(current + 1);
        tick();
      }, NEXT_AFTER);
    }

    function open() {
      if (!card.hidden) return;
      card.classList.remove("is-leaving");
      card.hidden = false;
      toggle.setAttribute("aria-expanded", "true");
      show(current);
      tick();
    }

    function close(byVisitor) {
      if (card.hidden) return;
      clearTimeout(timer);
      toggle.setAttribute("aria-expanded", "false");
      if (byVisitor) stored("closed");
      if (calm) { card.hidden = true; return; }
      card.classList.add("is-leaving");
      setTimeout(function () {
        card.hidden = true;
        card.classList.remove("is-leaving");
      }, 200);
    }

    slides.forEach(function (slide, i) {
      var title = slide.querySelector(".bx-hp__title");
      if (!title.id) title.id = "bx-hp-title-" + i;
    });
    toggle.addEventListener("click", function () {
      if (card.hidden) open(); else close(true);
    });
    root.querySelector("[data-bx-hp-close]").addEventListener("click", function () {
      close(true);
      toggle.focus();
    });
    dots.forEach(function (dot) {
      dot.addEventListener("click", function () {
        show(Number(dot.dataset.bxHpDot));
        tick();
      });
    });
    root.addEventListener("mouseenter", function () { paused = true; });
    root.addEventListener("mouseleave", function () { paused = false; });
    root.addEventListener("focusin", function () { paused = true; });
    root.addEventListener("focusout", function () { paused = false; });
    document.addEventListener("keydown", function (event) {
      if (event.key === "Escape" && !card.hidden) { close(true); toggle.focus(); }
    });

    /* once per visit, a little after the page is read; not over the cookie question */
    if (stored() !== "closed" && stored() !== "shown") {
      setTimeout(function () {
        var banner = document.getElementById("consent-banner");
        var asking = banner && banner.offsetParent !== null;
        if (asking || !card.hidden) {
          if (!calm) toggle.classList.add("is-calling");
          return;
        }
        stored("shown");
        open();
      }, OPEN_AFTER);
    }
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", start);
  else start();
})();
