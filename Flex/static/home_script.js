document.addEventListener('DOMContentLoaded', () => {
    // Using a silly dataset for demonstration
    const ctx = document.getElementById('funnyChart').getContext('2d');
  
    // Generate random data for 8 weeks
    const weeks = [...Array(8).keys()].map(i => i + 1); // [1..8]
    const gains = weeks.map(() => Math.floor(Math.random() * 15) + 5); 
    // random 5-20
  
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
  