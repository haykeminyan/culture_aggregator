document.addEventListener("DOMContentLoaded", function () {
  const mapDiv = document.getElementById("map");
  const title = document.getElementById("title").textContent;
  console.log(title);
  const lat = parseFloat(mapDiv.dataset.lat);
  const lng = parseFloat(mapDiv.dataset.lng);

  // Initialize the map
  const map = L.map("map").setView([lat, lng], 13);

  // Add OpenStreetMap tiles
  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution: "&copy; OpenStreetMap contributors",
  }).addTo(map);

  // Add a marker
  L.marker([lat, lng]).addTo(map).bindPopup(`${title}`).openPopup();
});
