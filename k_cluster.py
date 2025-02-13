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
    maps clusters to performance labels based on a composite score, writes the 
    processed output to output_file, and returns the results as a dict.
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
        # We assume:
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

        # Map the sorted clusters to performance labels
        # For example: best -> "good", middle -> "mediocre", worst -> "fatigued"
        label_mapping = {}
        performance_labels = ['good', 'mediocre', 'fatigued']
        for i, row in enumerate(centers_sorted.itertuples()):
            label_mapping[row.cluster] = performance_labels[i]
        print("Cluster to Performance Mapping:")
        print(label_mapping)

        # Assign performance labels to each rep based on its cluster
        df['performance'] = df['cluster'].map(label_mapping)

        # Convert the DataFrame back to a list of dictionaries for output
        processed_reps = df.to_dict(orient='records')
        results = {"processed_reps": processed_reps}

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
