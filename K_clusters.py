import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import MinMaxScaler

# =============================================================================
# 1. SIMULATE HISTORICAL DATA (Multiple Sets, Variable Reps)
# =============================================================================
np.random.seed(42)
historical_data = []
num_workouts = 5   # historical workouts
num_sets = 3       # sets per workout

# We simulate three performance states: "good", "mediocre", and "fatigued"
for workout in range(1, num_workouts + 1):
    for set_id in range(1, num_sets + 1):
        # Number of reps in this set (variable between 8 and 15)
        reps_in_set = np.random.randint(8, 16)
        for rep in range(1, reps_in_set + 1):
            state = np.random.choice(['good', 'mediocre', 'fatigued'], p=[0.5, 0.3, 0.2])
            if state == 'good':
                # Good reps: high range, minimal unwanted shoulder movement (0), fast upward velocity, controlled downward velocity
                rom = np.random.normal(130, 5)
                shoulder = 0  # ideal: no extra shoulder movement
                pav_up = np.random.normal(9, 1)
                pav_down = np.random.normal(4, 0.5)
            elif state == 'mediocre':
                # Mediocre reps: moderate values; shoulder movement could be 0 or 1
                rom = np.random.normal(115, 5)
                shoulder = np.random.choice([0, 1], p=[0.5, 0.5])
                pav_up = np.random.normal(7, 1)
                pav_down = np.random.normal(5, 0.5)
            else:  # fatigued
                # Fatigued reps: lower range, more shoulder movement, slower upward velocity, higher downward velocity (less control)
                rom = np.random.normal(100, 5)
                shoulder = 1
                pav_up = np.random.normal(5, 1)
                pav_down = np.random.normal(6, 0.5)
            
            historical_data.append({
                'workout_id': workout,
                'set_id': set_id,
                'rep_id': rep,
                'range_of_motion': rom,
                'shoulder_movement': shoulder,
                'peak_ang_vel_up': pav_up,
                'peak_ang_vel_down': pav_down
            })

hist_df = pd.DataFrame(historical_data)
print("Historical Data Sample:")
print(hist_df.head())

# =============================================================================
# 2. DATA PREPROCESSING & GLOBAL K-MEANS CLUSTERING
# =============================================================================
# Define the features (parameters) to use in clustering.
features = ['range_of_motion', 'shoulder_movement', 'peak_ang_vel_up', 'peak_ang_vel_down']

# Standardize the features
scaler = StandardScaler()
X_hist = scaler.fit_transform(hist_df[features])

# Choose 3 clusters (we expect these to roughly represent good, mediocre, fatigued)
num_clusters = 3
kmeans = KMeans(n_clusters=num_clusters, random_state=42)
hist_df['cluster'] = kmeans.fit_predict(X_hist)

# Get cluster centers in original scale for interpretation.
centers = scaler.inverse_transform(kmeans.cluster_centers_)
centers_df = pd.DataFrame(centers, columns=features)
print("\nGlobal Cluster Centers (Original Scale):")
print(centers_df)

# =============================================================================
# 3. MAP CLUSTERS TO PERFORMANCE LABELS
# =============================================================================
# We assume that higher range_of_motion (and ideally low shoulder_movement) is better.
# Therefore, we sort the cluster centers by range_of_motion (descending)

# Step 1: Normalize the cluster centers using MinMaxScaler for each feature.
scaler_mm = MinMaxScaler()
normalized_centers = scaler_mm.fit_transform(centers_df[features])
norm_centers_df = pd.DataFrame(normalized_centers, columns=features)
norm_centers_df['cluster'] = centers_df.index

# Step 2: Compute a composite score.
# Define weights for each feature.
# Here, we assume higher range_of_motion and peak_ang_vel_up are better,
# while lower shoulder_movement and lower peak_ang_vel_down are better.
weights = {
    'range_of_motion': 0.4,
    'peak_ang_vel_up': 0.3,
    'shoulder_movement': 0.2,
    'peak_ang_vel_down': 0.1
}

# Calculate composite score. Note: Since lower shoulder_movement and lower
# peak_ang_vel_down are better, we subtract their normalized values.
norm_centers_df['composite_score'] = (
    weights['range_of_motion'] * norm_centers_df['range_of_motion'] +
    weights['peak_ang_vel_up'] * norm_centers_df['peak_ang_vel_up'] -
    weights['shoulder_movement'] * norm_centers_df['shoulder_movement'] -
    weights['peak_ang_vel_down'] * norm_centers_df['peak_ang_vel_down']
)

# Step 3: Rank the clusters based on composite score.
centers_sorted = norm_centers_df.sort_values(by='composite_score', ascending=False)

# Map the sorted clusters to performance labels.
label_mapping = {}
labels = ['good', 'mediocre', 'fatigued']
for i, row in enumerate(centers_sorted.itertuples()):
    label_mapping[row.cluster] = labels[i]

print("Cluster to Performance Mapping (Based on Composite Score):")
print(label_mapping)

# Add a performance label column to the historical DataFrame.
hist_df['performance'] = hist_df['cluster'].map(label_mapping)

# =============================================================================
# 4. SIMULATE A NEW WORKOUT & ASSIGN CLUSTERS
# =============================================================================
new_workout_id = num_workouts + 1
new_workout_data = []
for set_id in range(1, num_sets + 1):
    reps_in_set = np.random.randint(8, 16)  # variable rep count
    for rep in range(1, reps_in_set + 1):
        state = np.random.choice(['good', 'mediocre', 'fatigued'], p=[0.5, 0.3, 0.2])
        if state == 'good':
            rom = np.random.normal(130, 5)
            shoulder = 0
            pav_up = np.random.normal(9, 1)
            pav_down = np.random.normal(4, 0.5)
        elif state == 'mediocre':
            rom = np.random.normal(115, 5)
            shoulder = np.random.choice([0, 1], p=[0.5, 0.5])
            pav_up = np.random.normal(7, 1)
            pav_down = np.random.normal(5, 0.5)
        else:
            rom = np.random.normal(100, 5)
            shoulder = 1
            pav_up = np.random.normal(5, 1)
            pav_down = np.random.normal(6, 0.5)
        
        new_workout_data.append({
            'workout_id': new_workout_id,
            'set_id': set_id,
            'rep_id': rep,
            'range_of_motion': rom,
            'shoulder_movement': shoulder,
            'peak_ang_vel_up': pav_up,
            'peak_ang_vel_down': pav_down
        })

new_df = pd.DataFrame(new_workout_data)

# Standardize new workout data using the previously fitted scaler.
X_new = scaler.transform(new_df[features])
new_df['cluster'] = kmeans.predict(X_new)
new_df['performance'] = new_df['cluster'].map(label_mapping)

# =============================================================================
# 5. FEEDBACK: OVERALL PERFORMANCE DISTRIBUTION IN THE NEW WORKOUT
# =============================================================================
print(f"\n--- New Workout (ID {new_workout_id}) Feedback ---")

# A. Count of Good, Mediocre, and Fatigued Reps
performance_counts = new_df['performance'].value_counts()
print("\nNumber of reps by performance level:")
for level in ['good', 'mediocre', 'fatigued']:
    count = performance_counts.get(level, 0)
    print(f"  {level.capitalize()} reps: {count}")

# B. Feature Comparison vs. Historical Data
# Compute historical averages for each performance category.
hist_perf_averages = hist_df.groupby('performance')[features].mean()

# Compute new workout averages for each performance category.
new_perf_averages = new_df.groupby('performance')[features].mean()

print("\nFeature Comparison (New Workout vs. Historical):")
for perf in ['good', 'mediocre', 'fatigued']:
    if perf in new_perf_averages.index:
        print(f"\nPerformance: {perf.capitalize()}")
        for feat in features:
            new_val = new_perf_averages.loc[perf, feat]
            hist_val = hist_perf_averages.loc[perf, feat] if perf in hist_perf_averages.index else np.nan
            diff = new_val - hist_val
            diff_percent = diff / hist_val * 100 if not np.isnan(hist_val) and hist_val != 0 else np.nan
            sign = "+" if diff >= 0 else "-"
            # just to see
            # print(f"  {feat}: New = {new_val:.2f}, Hist = {hist_val:.2f}, Diff = {sign}{abs(diff):.2f}")
            # what we actually want
            if diff_percent < -5 and feat != 'shoulder_movement':
                print(f"  Recommendation: Your {feat} has decreased significantly from historical averages. Consider focusing on this area during your next workout.")
            elif diff_percent > 5 and feat != 'shoulder_movement':
                print(f"  Recommendation: Your {feat} has improved significantly from historical averages. Try not to do this too much.")
            else:
                print("You are performing the same as historical averages, consider increasing weight soon.")
# =============================================================================
# 6. EARLY VS. LATE REP ANALYSIS WITHIN EACH SET
# =============================================================================
print("\nEarly vs. Late Rep Analysis for Each Set:")
set_groups = new_df.groupby('set_id')
for set_id, group in set_groups:
    group = group.sort_values('rep_id')
    n = len(group)
    # Split the set into early (first half) and late (second half)
    split_index = n // 2 if n >= 2 else 1
    early = group.iloc[:split_index]
    late = group.iloc[split_index:]
    
    early_means = early[features].mean()
    late_means = late[features].mean()
    
    print(f"\nSet {set_id}:")
    for feat in features:
        diff = late_means[feat] - early_means[feat]
        trend = "increased" if diff > 0 else "decreased"
        print(f"  {feat}: early = {early_means[feat]:.2f}, late = {late_means[feat]:.2f} ({trend} by {abs(diff):.2f})")
    
    # Generate a simple recommendation if significant deterioration is detected.
    # For example, if range_of_motion drops more than 5% from early to late reps.
    recommendation_given = False

    # Check each condition and print its recommendation.
    if early_means['range_of_motion'] > 0 and (early_means['range_of_motion'] - late_means['range_of_motion']) / early_means['range_of_motion'] > 0.05:
        print("  Recommendation: Your range of motion declines noticeably in later reps. Consider focusing on endurance or technique stabilization during later sets.")
        recommendation_given = True

    if early_means['peak_ang_vel_up'] > 0 and (early_means['peak_ang_vel_up'] - late_means['peak_ang_vel_up']) / early_means['peak_ang_vel_up'] > 0.05:
        print("  Recommendation: Your peak upward velocity has decreased significantly in later reps. Try to maintain power output throughout the set.")
        recommendation_given = True

    if early_means['peak_ang_vel_down'] > 0 and (early_means['peak_ang_vel_down'] - late_means['peak_ang_vel_down']) / early_means['peak_ang_vel_down'] > 0.05:
        print("  Recommendation: Your peak downward velocity has increased significantly in later reps. Focus on maintaining control during the eccentric phase.")
        recommendation_given = True

    if early_means['shoulder_movement'] < 1 and late_means['shoulder_movement'] > 0:
        print("  Recommendation: Your shoulder movement increases in later reps. Try to maintain stability and avoid compensatory movements.")
        recommendation_given = True

    # If none of the above conditions were met, print the default recommendation.
    if not recommendation_given:
        print("  Recommendation: Your performance is consistent throughout the set. Keep up the good work!")

# =============================================================================
# 7. OVERALL RECOMMENDATIONS BASED ON THE NEW WORKOUT ANALYSIS
# =============================================================================
