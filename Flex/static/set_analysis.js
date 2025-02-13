function computeSetMetrics(aggregatedData) {
    const reps = aggregatedData.reps;
    const totalReps = reps.length;
    if (totalReps === 0) {
      return null;
    }
  
    // Group reps: first 2/3 are early; last 1/3 are late.
    const earlyCount = Math.floor((2 / 3) * totalReps);
    const earlyReps = reps.slice(0, earlyCount);
    const lateReps = reps.slice(earlyCount);
  
    // Define how rep properties map to our feature names.
    const features = {
      range_of_motion: "max_pitch",
      peak_ang_vel_up: "max_gz_up",
      peak_ang_vel_down: "max_gz_down",
      shoulder_movement: "max_az"
    };
  
    // Compute mean values for each feature.
    const early_means = {};
    const late_means = {};
  
    for (const feat in features) {
      const property = features[feat];
      const earlySum = earlyReps.reduce((sum, rep) => sum + (rep[property] || 0), 0);
      const lateSum = lateReps.reduce((sum, rep) => sum + (rep[property] || 0), 0);
      early_means[feat] = earlyReps.length ? earlySum / earlyReps.length : 0;
      late_means[feat] = lateReps.length ? lateSum / lateReps.length : 0;
    }
  
    // Create metrics with differences and trends.
    const metrics = {};
    for (const feat in early_means) {
      const diff = late_means[feat] - early_means[feat];
      const trend = diff > 0 ? "increased" : "decreased";
      metrics[feat] = {
        early: early_means[feat],
        late: late_means[feat],
        difference: diff,
        trend: trend
      };
    }
  
    // Build recommendations based on significant changes.
    const recommendations = [];
    if (
      early_means["range_of_motion"] > 0 &&
      (early_means["range_of_motion"] - late_means["range_of_motion"]) / early_means["range_of_motion"] >
        0.05
    ) {
      recommendations.push(
        "Your range of motion declines noticeably in later reps. Consider focusing on endurance or technique stabilization during later sets."
      );
    }
    if (
      early_means["peak_ang_vel_up"] > 0 &&
      (early_means["peak_ang_vel_up"] - late_means["peak_ang_vel_up"]) / early_means["peak_ang_vel_up"] >
        0.05
    ) {
      recommendations.push(
        "Your peak upward velocity has decreased significantly in later reps. Try to maintain power output throughout the set."
      );
    }
    if (
      early_means["peak_ang_vel_down"] > 0 &&
      (early_means["peak_ang_vel_down"] - late_means["peak_ang_vel_down"]) / early_means["peak_ang_vel_down"] >
        0.05
    ) {
      recommendations.push(
        "Your peak downward velocity has increased significantly in later reps. Focus on maintaining control during the eccentric phase."
      );
    }
    if (early_means["shoulder_movement"] < 1 && late_means["shoulder_movement"] > 0) {
      recommendations.push(
        "Your shoulder movement increases in later reps. Try to maintain stability and avoid compensatory movements."
      );
    }
    if (recommendations.length === 0) {
      recommendations.push("Your performance is consistent throughout the set. Keep up the good work!");
    }
  
    return { metrics, recommendations, early_means, late_means };
  }
  