/* Live countdowns.
   - exhibition page: #countdown-timer flip clock (data-start / data-end, YYYY-MM-DD)
   - list cards: [data-status] pill on the picture and [data-countdown] on the ticket
   Dates are read as local calendar days; an exhibition runs until the end of its last day. */
(function () {
  "use strict";

  function day(s, endOfDay) {
    if (!s) return null;
    var m = /^(\d{4})-(\d{2})-(\d{2})/.exec(s);
    if (!m) {                                   // legacy formats, e.g. "May 1, 2026 at 10:00"
      var t = Date.parse(String(s).replace(" at ", ", "));
      return isNaN(t) ? null : new Date(t);
    }
    return endOfDay ? new Date(+m[1], m[2] - 1, +m[3], 23, 59, 59) : new Date(+m[1], m[2] - 1, +m[3]);
  }
  function phase(el, now) {
    var start = day(el.dataset.start), end = day(el.dataset.end, true);
    if (start && now < start) return { key: "soon", target: start };
    if (end && now <= end) return { key: "live", target: end };
    if (end) return { key: "ended" };
    return { key: start ? "live" : "none" };
  }
  function days(from, to) { return Math.ceil((to - from) / 86400000); }

  /* wording comes from window.I18N (base.html); numbers and plurals from Intl in the page language */
  var LANG = window.LANG || document.documentElement.lang || "en";
  function T(key) { return (window.I18N && window.I18N[key]) || key; }
  var rel, dur;
  try { rel = new Intl.RelativeTimeFormat(LANG, { numeric: "auto" }); } catch (e) { rel = new Intl.RelativeTimeFormat("en", { numeric: "auto" }); }
  try { dur = new Intl.NumberFormat(LANG, { style: "unit", unit: "day", unitDisplay: "long" }); } catch (e) { dur = new Intl.NumberFormat("en", { style: "unit", unit: "day", unitDisplay: "long" }); }
  function opensIn(n) { return n <= 1 ? T("Opens tomorrow") : T("Opens {when}").replace("{when}", rel.format(n, "day")); }
  function left(n) { return T("{time} left").replace("{time}", dur.format(n)); }

  function paintCard(now) {
    document.querySelectorAll("[data-status]").forEach(function (el) {
      var p = phase(el, now), text = "";
      el.classList.remove("is-live", "is-soon", "is-ended");
      if (p.key === "soon") { var n = days(now, p.target); text = opensIn(n); el.classList.add("is-soon"); }
      else if (p.key === "live") { text = T("Now on"); el.classList.add("is-live"); }
      else if (p.key === "ended") { text = T("Ended"); el.classList.add("is-ended"); }
      el.innerHTML = text ? '<i class="status-dot" aria-hidden="true"></i>' + text : "";
    });
    document.querySelectorAll("[data-countdown]").forEach(function (el) {
      var p = phase(el, now), text = "";
      if (p.key === "soon") { var n = days(now, p.target); text = opensIn(n); }
      else if (p.key === "live" && p.target) { var left_ = days(now, p.target); text = left_ <= 1 ? T("Last day") : left(left_); }
      else if (p.key === "ended") text = T("Ended");
      el.textContent = text;
    });
  }

  function pad(n) { return n < 10 ? "0" + n : String(n); }
  function paintFlip(el, now) {
    var p = phase(el, now);
    var label = el.querySelector("[data-flip-label]");
    var units = el.querySelectorAll("[data-u]");
    if (!units.length) {                         // old markup: plain text
      if (p.key === "ended") { el.textContent = "Event ended"; return false; }
      if (!p.target) { el.textContent = ""; return false; }
      var r = Math.max(0, p.target - now);
      el.textContent = Math.floor(r / 864e5) + "d " + Math.floor(r / 36e5) % 24 + "h " + Math.floor(r / 6e4) % 60 + "m " + Math.floor(r / 1e3) % 60 + "s left";
      return true;
    }
    if (p.key === "ended" || !p.target) {
      el.classList.add("is-ended");
      if (label) label.textContent = p.key === "ended" ? T("This exhibition has ended") : "";
      return false;
    }
    if (label) label.textContent = p.key === "soon" ? T("Opens in") : T("Closes in");
    var rest = Math.max(0, p.target - now);
    var v = { d: Math.floor(rest / 864e5), h: Math.floor(rest / 36e5) % 24, m: Math.floor(rest / 6e4) % 60, s: Math.floor(rest / 1e3) % 60 };
    units.forEach(function (u) {
      var next = u.dataset.u === "d" ? String(v.d) : pad(v[u.dataset.u]);
      if (u.textContent !== next) {
        u.textContent = next;
        u.classList.remove("is-flipping"); void u.offsetWidth; u.classList.add("is-flipping");
      }
    });
    return true;
  }

  document.addEventListener("DOMContentLoaded", function () {
    var flip = document.getElementById("countdown-timer");
    var tick = function () {
      var now = new Date();
      paintCard(now);
      return flip ? paintFlip(flip, now) : false;
    };
    var running = tick();
    if (running) {
      var id = setInterval(function () { if (!document.hidden && !tick()) clearInterval(id); }, 1000);
    } else if (document.querySelector("[data-status], [data-countdown]")) {
      setInterval(function () { if (!document.hidden) paintCard(new Date()); }, 60000);
    }
  });
})();
