// Global chart reference
let tutChart; 
let tutData = [];   // Will store sequential TUT data points
let fetchCount = 0; // We'll use an incremental x-axis

function highlightChange(element) {
  element.classList.add('flash');
  setTimeout(() => element.classList.remove('flash'), 1000);
}

function initTUTChart() {
  const ctx = document.getElementById('tutChart');
  tutChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: [],     // x-axis: will fill with fetch counts or timestamps
      datasets: [{
        label: 'Time Under Tension (s)',
        data: [],      // we'll push TUT values here
        borderColor: '#4ea7ff',
        backgroundColor: 'rgba(78, 167, 255, 0.3)',
        fill: true,
        tension: 0.3
      }]
    },
    options: {
      scales: {
        y: {
          beginAtZero: true,
          title: { display: true, text: 'TUT (seconds)' }
        },
        x: {
          title: { display: true, text: 'Fetch Count' }
        }
      },
      plugins: {
        legend: { display: false }
      }
    }
  });
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
      // Range of Motion
      let romElem = document.getElementById('rom');
      if (romElem) {
        romElem.textContent = `Range of Motion: ${data.range_of_motion}`;
        highlightChange(romElem);
      }

      // Swinging
      let swingElem = document.getElementById('swing');
      if (swingElem) {
        swingElem.textContent = `Swinging: ${data.swinging}`;
        highlightChange(swingElem);
      }

      // TUT chart
      fetchCount++;
      const newTUT = data.time_under_tension; // numeric
      if (tutChart) {
        tutChart.data.labels.push(fetchCount);
        tutChart.data.datasets[0].data.push(newTUT);
        tutChart.update();
      }
    })
    .catch(err => console.error("Error fetching ML data:", err));
}

// Initialize chart & start fetching
document.addEventListener('DOMContentLoaded', () => {
  // If the TUT chart canvas is on this page, init the chart
  if (document.getElementById('tutChart')) {
    initTUTChart();
    fetchMLData();
    setInterval(fetchMLData, 5000);
  }
});
