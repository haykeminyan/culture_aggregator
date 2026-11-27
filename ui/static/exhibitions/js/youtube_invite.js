/* "Share the channel": the system share sheet where there is one, otherwise copy the link */
(function () {
  'use strict';
  document.querySelectorAll('[data-bx-yt-share]').forEach(function (button) {
    var label = button.querySelector('span');
    var text = label.textContent;
    button.addEventListener('click', function () {
      var url = button.dataset.url;
      if (navigator.share) {
        navigator.share({ title: button.dataset.title, url: url }).catch(function () {});
        return;
      }
      if (navigator.clipboard) {
        navigator.clipboard.writeText(url).then(function () {
          label.textContent = button.dataset.copied;
          setTimeout(function () { label.textContent = text; }, 2000);
        });
      } else {
        window.open(url, '_blank', 'noopener');
      }
    });
  });
})();
