function displayBarChart(analysis) {
    
    const ctx = document.getElementById('repComparisonChart').getContext('2d');
  
    
    const features = Object.keys(analysis.metrics);
    const earlyData = features.map(f => analysis.metrics[f].early);
    const lateData = features.map(f => analysis.metrics[f].late);
  
    
    if (window.repComparisonChart) {
      window.repComparisonChart.destroy();
    }
  
   
    window.repComparisonChart = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: features, 
        datasets: [
          {
            label: 'Early Reps',
            data: earlyData,
            backgroundColor: 'rgba(54, 162, 235, 0.5)', 
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
  