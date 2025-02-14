import json
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler, MinMaxScaler

# File paths
INPUT_FILE_PATH = "/home/ubuntu/metrics.json"
OUTPUT_FILE_PATH = "/home/ubuntu/processed_output.json"

def run_clustering(input_file=INPUT_FILE_PATH, output_file=OUTPUT_FILE_PATH):
    """
    Reads metrics from input_file, performs preprocessing and K-Means clustering,
    maps clusters to performance labels based on a composite score, performs additional
    comparisons between current and historical performance metrics, writes the 
    processed output (including coaching observations) to output_file, and returns the results as a dict.
    """
    try:
        # Read input JSON file
        with open(input_file, "r") as file:
            data = json.load(file)

        # Extract rep data
        reps = data.get("metrics", {}).get("reps", [])
        if not reps:
            raise ValueError("No rep data found in metrics.json")

        # Create DataFrame from reps
        df = pd.DataFrame(reps)
        # Define the features to use in clustering
        features = ['max_pitch', 'max_az', 'max_gz_up', 'max_gz_down']
        missing_features = [feat for feat in features if feat not in df.columns]
        if missing_features:
            raise ValueError(f"Missing features in input data: {missing_features}")

        # --- Data Preprocessing ---
        # Standardize the features using StandardScaler
        scaler = StandardScaler()
        X = scaler.fit_transform(df[features])

        # --- K-Means Clustering ---
        # Use 3 clusters to represent performance levels: good, mediocre, fatigued
        num_clusters = 3
        kmeans = KMeans(n_clusters=num_clusters, random_state=42, n_init=10)
        df['cluster'] = kmeans.fit_predict(X)

        # Get cluster centers in the original scale for interpretation
        centers = scaler.inverse_transform(kmeans.cluster_centers_)
        centers_df = pd.DataFrame(centers, columns=features)
        print("\nGlobal Cluster Centers (Original Scale):")
        print(centers_df)

        # --- Map Clusters to Performance Labels ---
        # Normalize the cluster centers using MinMaxScaler so that each feature is on [0,1]
        scaler_mm = MinMaxScaler()
        normalized_centers = scaler_mm.fit_transform(centers_df[features])
        norm_centers_df = pd.DataFrame(normalized_centers, columns=features)
        norm_centers_df['cluster'] = centers_df.index

        # Compute a composite score for each cluster.
        # Assumptions:
        #   • Higher max_pitch and max_gz_up are better.
        #   • Lower max_az and max_gz_down are better.
        weights = {
            'max_pitch': 0.4,
            'max_gz_up': 0.3,
            'max_az': 0.2,
            'max_gz_down': 0.1
        }
        norm_centers_df['composite_score'] = (
            weights['max_pitch'] * norm_centers_df['max_pitch'] +
            weights['max_gz_up'] * norm_centers_df['max_gz_up'] -
            weights['max_az'] * norm_centers_df['max_az'] -
            weights['max_gz_down'] * norm_centers_df['max_gz_down']
        )

        # Rank clusters based on composite score (highest = best performance)
        centers_sorted = norm_centers_df.sort_values(by='composite_score', ascending=False)

        # Map the sorted clusters to performance labels:
        # Best -> "good", middle -> "mediocre", worst -> "fatigued"
        label_mapping = {}
        performance_labels = ['good', 'mediocre', 'fatigued']
        for i, row in enumerate(centers_sorted.itertuples()):
            label_mapping[row.cluster] = performance_labels[i]
        print("Cluster to Performance Mapping:")
        print(label_mapping)

        # Assign performance labels to each rep based on its cluster
        df['performance'] = df['cluster'].map(label_mapping)

        # --- Additional Analysis: Compare new vs. historical performance metrics ---
        # Compute new performance ratios from current reps (as proportions)
        new_perf_ratio = df['performance'].value_counts(normalize=True).to_dict()

        # Define the additional metrics to compute averages for
        extra_metrics = ['peak_ang_vel_up', 'range_of_motion', 'shoulder_movement', 'peak_ang_vel_down']
        # Check if these metrics are present. If not, skip average-based analysis.
        available_extra = [m for m in extra_metrics if m in df.columns]
        if available_extra:
            new_perf_averages = df.groupby("performance")[available_extra].mean()
        else:
            new_perf_averages = pd.DataFrame()

        # Try to load historical performance ratios and averages from the input JSON.
        # (They should be provided in the JSON under these keys if available.)
        hist_perf_ratio = data.get("historical_perf_ratio", {})
        # Expect historical averages to be stored as a dict of dicts.
        hist_perf_averages = data.get("historical_perf_averages", {})
        if hist_perf_averages:
            # Convert to DataFrame for easier comparison.
            hist_perf_averages = pd.DataFrame.from_dict(hist_perf_averages, orient='index')

        # Prepare a list to accumulate coaching observations.
        coaching_observations = []

        # 1. Compare fatigued ratios:
        if new_perf_ratio.get('fatigued', 0) > hist_perf_ratio.get('fatigued', 0):
            msg = (
                "You performed a higher percentage of fatigued reps compared to your historical data. "
                "Consider reviewing your recovery protocols or adjusting your workout intensity."
            )
            coaching_observations.append(msg)
            print("  - " + msg)
        else:
            msg = (
                "Your percentage of fatigued reps is in line with or below your historical average. "
                "Keep up the good work on recovery."
            )
            coaching_observations.append(msg)
            print("  - " + msg)

        # 2. Compare averages for 'good' reps if extra metrics are available and historical data exists
        if not new_perf_averages.empty and ('good' in new_perf_averages.index) and ('good' in hist_perf_averages.index):
            # 2a. Peak upward velocity
            if new_perf_averages.loc['good', 'peak_ang_vel_up'] < hist_perf_averages.loc['good', 'peak_ang_vel_up']:
                msg = (
                    "For your 'good' reps, the peak upward velocity is slightly lower than usual. "
                    "You might consider incorporating power or speed work to improve explosive strength."
                )
                coaching_observations.append(msg)
                print("  - " + msg)
            # 2b. Range of Motion
            if new_perf_averages.loc['good', 'range_of_motion'] < 0.95 * hist_perf_averages.loc['good', 'range_of_motion']:
                msg = (
                    "Your average range of motion for 'good' reps has decreased more than 5% compared to your historical average. "
                    "This could indicate tightness or fatigue. Make sure to include mobility and warm-up exercises."
                )
                coaching_observations.append(msg)
                print("  - " + msg)
            # 2c. Shoulder Movement
            if new_perf_averages.loc['good', 'shoulder_movement'] > 1.05 * hist_perf_averages.loc['good', 'shoulder_movement']:
                msg = (
                    "Your shoulder movement for 'good' reps is higher than your historical average. "
                    "This might indicate you are compensating with your shoulder. Focus on strict form to isolate the biceps."
                )
                coaching_observations.append(msg)
                print("  - " + msg)

        # 3. Compare averages for 'fatigued' reps
        if not new_perf_averages.empty and ('fatigued' in new_perf_averages.index) and ('fatigued' in hist_perf_averages.index):
            # 3a. Range of Motion
            if new_perf_averages.loc['fatigued', 'range_of_motion'] < hist_perf_averages.loc['fatigued', 'range_of_motion']:
                msg = (
                    "Your range of motion in 'fatigued' reps is lower than your historical norm. "
                    "This suggests your form breaks down more than usual once fatigued. Consider lighter weights or more rest."
                )
                coaching_observations.append(msg)
                print("  - " + msg)
            # 3b. Shoulder Movement
            if new_perf_averages.loc['fatigued', 'shoulder_movement'] > hist_perf_averages.loc['fatigued', 'shoulder_movement']:
                msg = (
                    "Your shoulder involvement in 'fatigued' reps is higher than usual. "
                    "You may be compensating with the shoulder. Focus on strict technique and biceps isolation."
                )
                coaching_observations.append(msg)
                print("  - " + msg)
            # 3c. Downward Velocity
            if new_perf_averages.loc['fatigued', 'peak_ang_vel_down'] > hist_perf_averages.loc['fatigued', 'peak_ang_vel_down']:
                msg = (
                    "Your peak downward velocity on fatigued reps is higher than historical averages. "
                    "A faster eccentric might lead to less muscle control or potential injury risk. Try slowing the negative phase."
                )
                coaching_observations.append(msg)
                print("  - " + msg)

        # 4. Additional Observations based on fatigued ratio difference
        fatigued_diff = (new_perf_ratio.get('fatigued', 0) - hist_perf_ratio.get('fatigued', 0)) * 100
        print("\nAdditional Observations:")
        if fatigued_diff > 10:  # e.g., a 10% higher fatigued ratio
            msg = f"There's a significant (+{fatigued_diff:.1f}%) jump in fatigued reps. Consider shorter sets, longer rest, or adjusting weight."
            coaching_observations.append(msg)
            print("  - " + msg)
        elif fatigued_diff < -5:  # e.g., 5% lower fatigued ratio
            msg = f"Nice improvement! You reduced your fatigued reps by {-fatigued_diff:.1f}%. Keep up the consistent training and recovery."
            coaching_observations.append(msg)
            print("  - " + msg)

        # 5. (Optional) Define change thresholds for further analysis
        change_thresholds = {
            'range_of_motion': 0.90,   # 10% drop
            'peak_ang_vel_up': 0.90,   # 10% drop
            'peak_ang_vel_down': 1.10, # 10% higher (faster negative)
            'shoulder_movement': 1.10  # 10% more shoulder movement
        }
        # You could add more observations here based on these thresholds.

        # --- Prepare Final Results ---
        # Convert the DataFrame back to a list of dictionaries for output
        processed_reps = df.to_dict(orient='records')
        results = {
            "processed_reps": processed_reps,
            "new_perf_ratio": new_perf_ratio,
            "coaching_observations": coaching_observations
        }

        # Optionally include new_perf_averages (converted to dict) if available
        if not new_perf_averages.empty:
            results["new_perf_averages"] = new_perf_averages.to_dict(orient='index')

        # Save the processed results to the output JSON file
        with open(output_file, "w") as file:
            json.dump(results, file, indent=4)

        print("Processing completed successfully. Output saved to processed_output.json.")
        return results

    except Exception as e:
        error_result = {"error": str(e)}
        with open(output_file, "w") as file:
            json.dump(error_result, file, indent=4)
        print(f"Error processing data: {e}")
        return error_result

if __name__ == '__main__':
    run_clustering()
