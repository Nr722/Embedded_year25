from flask import Flask, request, jsonify
import json
import os
import threading
from flask_cors import CORS
from k_means_clustering import run_clustering  # Import the clustering function

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

METRICS_FILE_PATH = "/home/ubuntu/metrics.json"
OUTPUT_FILE_PATH = "/home/ubuntu/processed_output.json"

def background_clustering():
    """
    Function to run clustering in the background.
    This function runs on a separate thread.
    """
    run_clustering(METRICS_FILE_PATH, OUTPUT_FILE_PATH)

@app.route('/save_metrics', methods=['POST'])
def save_metrics():
    try:
        # Remove any existing processed output file.
        if os.path.exists(OUTPUT_FILE_PATH):
            os.remove(OUTPUT_FILE_PATH)

        data = request.json  # Get JSON payload
        if not data:
            return jsonify({"status": "error", "message": "No data received"}), 400

        # Save the metrics data to a file.
        with open(METRICS_FILE_PATH, "w") as json_file:
            json.dump(data, json_file, indent=4)

        # Start clustering in a background thread.
        clustering_thread = threading.Thread(target=background_clustering)
        clustering_thread.start()

        # Immediately return a response to the client.
        return jsonify({
            "status": "processing",
            "message": "Metrics saved. Clustering is in progress."
        })

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/get_processed_results", methods=["GET"])
def get_processed_results():
    try:
        # Check if the processed output file is available.
        if not os.path.exists(OUTPUT_FILE_PATH):
            return jsonify({
                "status": "processing",
                "message": "Processing not complete yet."
            }), 202  # 202 Accepted indicates that the request is being processed
        else:
            with open(OUTPUT_FILE_PATH, "r") as output_file:
                processed_data = json.load(output_file)
                # Instead of sending per rep data, we only send the aggregated coaching message.
                if "coaching_observations" in processed_data:
                    # Join all messages into a single string.
                    msg = "\n".join(processed_data["coaching_observations"])
                else:
                    msg = "No coaching observations available."
                return jsonify({
                    "status": "success",
                    "message": msg
                })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 404

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
