function displayBarChart(analysis) {
    // Get the canvas element
    const ctx = document.getElementById('repComparisonChart').getContext('2d');
  
    // Extract feature names and their early/late values
    const features = Object.keys(analysis.metrics);
    const earlyData = features.map(f => analysis.metrics[f].early);
    const lateData = features.map(f => analysis.metrics[f].late);
  
    // (Optional) Clear any previous chart instance if you are redrawing
    if (window.repComparisonChart) {
      window.repComparisonChart.destroy();
    }
  
    // Create the bar chart
    window.repComparisonChart = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: features, // e.g., ["Range of Motion", "Peak Velocity", ...]
        datasets: [
          {
            label: 'Early Reps',
            data: earlyData,
            backgroundColor: 'rgba(54, 162, 235, 0.5)', // or any preferred color
            borderColor: 'rgba(54, 162, 235, 1)',
            borderWidth: 1
          },
          {
            label: 'Late Reps',
            data: lateData,
            backgroundColor: 'rgba(255, 99, 132, 0.5)',
            borderColor: 'rgba(255, 99, 132, 1)',
            borderWidth: 1
          }
        ]
      },
      options: {
        responsive: true,
        scales: {
          y: {
            beginAtZero: true, 
            title: {
              display: true,
              text: 'Metric Value'
            }
          },
          x: {
            title: {
              display: true,
              text: 'Metrics'
            }
          }
        },
        plugins: {
          title: {
            display: true,
            text: 'Comparison of Early vs. Late Rep Metrics'
          }
        }
      }
    });
  }
  