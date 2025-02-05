document.addEventListener('DOMContentLoaded', () => {
  const ctx = document.getElementById('funnyChart').getContext('2d');

  // We'll do 8 weeks
  const weeks = [...Array(8).keys()].map(i => i + 1); // [1..8]

  // Gains as an exponential function
  const base = 5;
  const factor = 1.35;
  const gains = weeks.map(week => {
    // e.g. 5 * (1.35^week), plus a small random offset for variety
    const exponentVal = base * Math.pow(factor, week);
    const randomOffset = Math.floor(Math.random() * 3); // 0..2
    return Math.floor(exponentVal) + randomOffset;
  });

  new Chart(ctx, {
    type: 'line',
    data: {
      labels: weeks.map(w => `Week ${w}`),
      datasets: [{
        label: 'Gains (arbitrary units)',
        data: gains,
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
          title: { display: true, text: 'Gains' }
        },
        x: {
          title: { display: true, text: 'Time Using FLEX (weeks)' }
        }
      },
      plugins: {
        legend: { display: false }
      }
    }
  });
});
