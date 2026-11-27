/* Donate to Baregorc: the bottom-left pomegranate opens the card; "Other" shows an amount field. */
(function () {
  "use strict";
  var doc = document;

  doc.querySelectorAll("[data-bx-dn-form]").forEach(function (form) {
    var custom = form.querySelector("[data-bx-dn-custom]");
    var input = custom && custom.querySelector("input");
    var sync = function () {
      var other = form.querySelector("[data-bx-dn-other]");
      var on = other && other.checked;
      if (custom) custom.hidden = !on;
      if (input) input.required = !!on;
      if (on && input) input.focus();
    };
    form.addEventListener("change", function (e) { if (e.target.name === "amount") sync(); });
    form.addEventListener("submit", function () {
      var go = form.querySelector(".bx-dn-form__go");
      if (go) { go.disabled = true; go.classList.add("is-busy"); }
    });
    window.addEventListener("pageshow", function () {
      var go = form.querySelector(".bx-dn-form__go");
      if (go) { go.disabled = false; go.classList.remove("is-busy"); }
    });
    sync();
  });

  var root = doc.querySelector("[data-bx-dn]");
  if (!root) return;
  var card = root.querySelector(".bx-dn__card");
  var toggle = root.querySelector("[data-bx-dn-toggle]");
  var open = function () {
    card.hidden = false;
    card.classList.remove("is-leaving");
    toggle.setAttribute("aria-expanded", "true");
    var first = card.querySelector("input[name=amount]:checked") || card.querySelector("input");
    if (first) first.focus({ preventScroll: true });
  };
  var close = function () {
    if (card.hidden) return;
    toggle.setAttribute("aria-expanded", "false");
    card.classList.add("is-leaving");
    setTimeout(function () { card.hidden = true; card.classList.remove("is-leaving"); }, 190);
  };
  toggle.addEventListener("click", function () { card.hidden ? open() : close(); });
  root.querySelector("[data-bx-dn-close]").addEventListener("click", function () { close(); toggle.focus(); });
  doc.addEventListener("keydown", function (e) { if (e.key === "Escape" && !card.hidden) { close(); toggle.focus(); } });
  doc.addEventListener("click", function (e) { if (!card.hidden && !root.contains(e.target)) close(); });
  if (!doc.querySelector(".donate-stripe")) doc.querySelectorAll('a[href$="#donate"]').forEach(function (a) {
    a.addEventListener("click", function (e) { e.preventDefault(); open(); });
  });
})();
