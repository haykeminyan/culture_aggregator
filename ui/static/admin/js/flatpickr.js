/* global flatpickr */

document.addEventListener("DOMContentLoaded", function () {
  flatpickr("#start_date", {
    enableTime: true,
    dateFormat: "Y-m-d H:i",
  });

  flatpickr("#end_date", {
    enableTime: true,
    dateFormat: "Y-m-d H:i",
  });
});
