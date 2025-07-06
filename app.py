import os
import shutil
from flask import Flask, request, send_file, jsonify
from werkzeug.utils import secure_filename
from flask_cors import CORS
from random import random
from PIL import Image
import glob

from modules.detect_boulders import detect_boulders
from modules.cluster_boulders import cluster_boulders
from modules.generate_stats import generate_stats
from modules.generate_heatmap import generate_heatmap
from modules.estimate_source import estimate_source
from modules.generate_pdf_report import generate_pdf
from modules.generate_heatmap_json import generate_heatmap_json
from modules.detect_landslides import detect_landslides

# App Initialization
app = Flask(__name__)
CORS(app)  # Enable CORS for cross-origin frontend calls

app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['STATIC_FOLDER'] = 'static'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['STATIC_FOLDER'], exist_ok=True)

def cleanup_previous_results():
    try:
        files_to_remove = [
            'preview.jpg',
            'boulders_detected.jpg',
            'landslides_detected.jpg',
            'clustered_boulders_plot.jpg',
            'risk_heatmap.jpg',
            'boulders_with_source.jpg',
            'report.pdf',
            'boulder_data_clustered.csv',
            'boulder_points.json',
            'stats_summary.txt'
        ]
        for filename in files_to_remove:
            filepath = os.path.join(app.config['STATIC_FOLDER'], filename)
            if os.path.exists(filepath):
                os.remove(filepath)
                print(f"[🗑️] Removed old file: {filename}")

        csv_files = glob.glob("boulder_data*.csv")
        for csv_file in csv_files:
            if os.path.exists(csv_file):
                os.remove(csv_file)
                print(f"[🗑️] Removed old CSV: {csv_file}")

        print("[✅] Cleanup completed successfully")

    except Exception as e:
        print(f"[⚠️] Error during cleanup: {str(e)}")

def convert_tif_to_jpg(image_path):
    if image_path.lower().endswith('.tif'):
        try:
            img = Image.open(image_path)
            if img.mode != 'RGB':
                img = img.convert('RGB')
            converted_path = os.path.join(app.config['UPLOAD_FOLDER'], 'converted_image.jpg')
            img.save(converted_path, "JPEG")
            print(f"[✅] Converted .tif to .jpg: {converted_path}")
            return converted_path
        except Exception as e:
            print(f"[ERROR] Unable to convert .tif image: {e}")
            return None
    return image_path

@app.route('/')
def home():
    return "✅ SOMA Backend is live!"

@app.route('/analyze', methods=['POST'])
def analyze():
    cleanup_previous_results()

    if 'image' not in request.files:
        return jsonify({"error": "No file part in the request."}), 400

    file = request.files['image']
    if not file.filename:
        return jsonify({"error": "No file selected for upload."}), 400

    try:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        print(f"[📁] Saved uploaded file: {filepath}")

        processed_filepath = convert_tif_to_jpg(filepath)
        if not processed_filepath:
            return jsonify({"error": "Failed to process .tif image."}), 500

        preview_path = os.path.join(app.config['STATIC_FOLDER'], 'preview.jpg')
        shutil.copy(processed_filepath, preview_path)
        print(f"[🖼️] Created preview: {preview_path}")

        print("[🔬] Starting analysis pipeline...")
        detect_boulders(processed_filepath)
        cluster_boulders()
        generate_stats()
        generate_heatmap()
        estimate_source()
        detect_landslides(processed_filepath)
        generate_pdf()
        generate_heatmap_json()
        print("[✅] Analysis pipeline completed")

        stats_text = ""
        stats_file = os.path.join(app.config['STATIC_FOLDER'], 'stats_summary.txt')
        if os.path.exists(stats_file):
            with open(stats_file, 'r', encoding='utf-8') as f:
                stats_text = f.read()
            print("[📊] Loaded stats")

        return jsonify({
            "status": "success",
            "preview_url": "/static/preview.jpg",
            "report_url": "/download-report",
            "stats_summary": stats_text,
            "random": random()
        })

    except Exception as e:
        print(f"[💥] Pipeline Error: {str(e)}")
        return jsonify({"error": f"Pipeline Error: {str(e)}"}), 500

@app.route('/download-report')
def download_report():
    report_path = os.path.join(app.config['STATIC_FOLDER'], 'report.pdf')
    if os.path.exists(report_path):
        return send_file(report_path, as_attachment=True)
    return jsonify({"error": "Report file not found."}), 404

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
