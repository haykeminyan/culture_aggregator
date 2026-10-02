/* Exhibition location (detail page only). Does nothing on pages without #map or valid coordinates. */
document.addEventListener("DOMContentLoaded", function () {
  "use strict";
  var mapDiv = document.getElementById("map");
  if (!mapDiv || !window.L) return;

  var lat = parseFloat(mapDiv.dataset.lat);
  var lng = parseFloat(mapDiv.dataset.lng);
  if (!isFinite(lat) || !isFinite(lng)) {
    (mapDiv.closest(".exd-map") || mapDiv).hidden = true;
    return;
  }
  var titleEl = document.getElementById("title");
  var title = titleEl ? titleEl.textContent.trim() : "";

  var map = L.map(mapDiv, { scrollWheelZoom: false }).setView([lat, lng], 14);
  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution: "&copy; OpenStreetMap contributors",
    maxZoom: 19,
  }).addTo(map);

  var pin = L.divIcon({ className: "ex-pin", html: "<span></span>", iconSize: [26, 26], iconAnchor: [13, 31], popupAnchor: [0, -30] });
  var popup = document.createElement("div");
  popup.textContent = title;                     // text, not HTML
  L.marker([lat, lng], { icon: pin, title: title, alt: title }).addTo(map).bindPopup(popup).openPopup();

  map.once("focus click", function () { map.scrollWheelZoom.enable(); });  // page scroll is not hijacked
});
