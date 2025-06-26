import os
import shutil
from flask import Flask, request, render_template, send_file
from werkzeug.utils import secure_filename
from random import random
from PIL import Image

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
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['STATIC_FOLDER'] = 'static'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['STATIC_FOLDER'], exist_ok=True)

def convert_tif_to_jpg(image_path):
    """
    Converts a .tif image to .jpg and returns the converted file path.
    """
    if image_path.lower().endswith('.tif'):
        try:
            img = Image.open(image_path)

            # Convert to RGB if necessary
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

@app.route('/', methods=['GET', 'POST'])
def index():
    stats_text = "No stats available yet. Upload an image to generate results."

    if request.method == 'POST':
        if 'image' not in request.files:
            return "Error: No file part in the request."
        file = request.files['image']

        if not file.filename:
            return "Error: No file selected for upload."

        if file:
            try:
                # Save uploaded image
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)

                # Handle .tif conversion if needed
                processed_filepath = convert_tif_to_jpg(filepath)
                if not processed_filepath:
                    return "Error: Failed to process .tif image."

                # Generate a preview image for the UI
                preview_path = os.path.join(app.config['STATIC_FOLDER'], 'preview.jpg')
                shutil.copy(processed_filepath, preview_path)

                # Full Detection Pipeline
                detect_boulders(processed_filepath)
                cluster_boulders()
                generate_stats()
                generate_heatmap()
                estimate_source()
                generate_pdf()
                generate_heatmap_json()
                detect_landslides(processed_filepath)

                # Load stats if available
                stats_file = os.path.join(app.config['STATIC_FOLDER'], 'stats_summary.txt')
                if os.path.exists(stats_file):
                    with open(stats_file, 'r', encoding='utf-8') as f:
                        stats_text = f.read()

            except Exception as e:
                return f"Pipeline Error: {str(e)}"

    return render_template('index.html', stats_text=stats_text, random=random)

@app.route('/download-report')
def download_report():
    report_path = os.path.join(app.config['STATIC_FOLDER'], 'report.pdf')
    if os.path.exists(report_path):
        return send_file(report_path, as_attachment=True)
    return "Error: Report file not found."

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
