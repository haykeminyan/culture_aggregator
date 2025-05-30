document.addEventListener("DOMContentLoaded", () => {
  const timerEl = document.getElementById("countdown-timer");
  if (!timerEl) return;

  const endDateStr = timerEl.dataset.end;
  if (!endDateStr) {
    timerEl.innerHTML = "No end date provided";
    return;
  }

  const endBad = endDateStr;
  const cleaned = endBad.replace(" at ", ", ");

  // Create Date object
  const date = new Date(cleaned);

  // Get timestamp in milliseconds
  const end = date.getTime();
  const interval = setInterval(() => {
    const now = new Date().getTime();
    const diff = end - now;

    if (diff <= 0) {
      clearInterval(interval);
      timerEl.innerHTML = "🎉 Event ended!";
      return;
    }

    const days = Math.floor(diff / (1000 * 60 * 60 * 24));
    const hours = Math.floor((diff / (1000 * 60 * 60)) % 24);
    const minutes = Math.floor((diff / (1000 * 60)) % 60);
    const seconds = Math.floor((diff / 1000) % 60);

    timerEl.innerHTML = `${days}d ${hours}h ${minutes}m ${seconds}s left`;
  }, 1000);
});
