/* Galleries.
   - exhibition page: slides with arrows, dots, keyboard and gentle autoplay
   - list cards: cross-fade, and the card flips through its photos while you hover it */
document.addEventListener("DOMContentLoaded", function () {
  "use strict";
  if (!window.Swiper) return;
  var reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;

  document.querySelectorAll(".swiper").forEach(function (el) {
    var count = el.querySelectorAll(".swiper-slide").length;
    var inCard = !!el.closest(".ex-card");
    var dots = el.querySelector(".swiper-pagination");
    var next = el.querySelector(".swiper-button-next"), prev = el.querySelector(".swiper-button-prev");

    var swiper = new Swiper(el, {
      loop: count > 1,
      speed: reduce ? 0 : (inCard ? 900 : 700),
      slidesPerView: 1,
      spaceBetween: 0,
      allowTouchMove: count > 1,
      grabCursor: count > 1,
      effect: inCard ? "fade" : "slide",
      fadeEffect: { crossFade: true },
      pagination: dots ? { el: dots, clickable: true } : false,
      navigation: next && prev ? { nextEl: next, prevEl: prev } : false,
      keyboard: inCard ? false : { enabled: true, onlyInViewport: true },
      autoplay: count > 1 && !reduce ? { delay: inCard ? 1600 : 5500, disableOnInteraction: false, pauseOnMouseEnter: !inCard } : false,
      a11y: { enabled: true },
    });

    if (inCard && swiper.autoplay && swiper.autoplay.running) {
      swiper.autoplay.stop();
      var card = el.closest(".ex-card");
      card.addEventListener("mouseenter", function () { swiper.slideNext(); swiper.autoplay.start(); });
      card.addEventListener("mouseleave", function () { swiper.autoplay.stop(); });
    }
  });
});
