function highlightChange(element) {
  element.classList.add('flash');
  setTimeout(() => element.classList.remove('flash'), 1000);
}

function fetchMLData() {
  fetch('/ml_feedback')
    .then(res => {
      if (!res.ok) {
        throw new Error(`Server error ${res.status}`);
      }
      return res.json();
    })
    .then(data => {
      let romElem = document.getElementById('rom');
      let tutElem = document.getElementById('tut');
      let swingElem = document.getElementById('swing');

      romElem.textContent = `Range of Motion: ${data.range_of_motion}`;
      highlightChange(romElem);

      tutElem.textContent = `Time Under Tension: ${data.time_under_tension} s`;
      highlightChange(tutElem);

      swingElem.textContent = `Swinging: ${data.swinging}`;
      highlightChange(swingElem);

    })
    .catch(err => console.error("Error fetching ML data:", err));
}

// Trigger fetch once DOM loaded, then repeat every 5s
document.addEventListener('DOMContentLoaded', () => {
  fetchMLData();
  setInterval(fetchMLData, 5000);
});
