from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from datetime import datetime
import os

def generate_pdf(timestamp=None, output_path=None):
    """
    Generates a PDF report summarizing boulder detection, clustering, and risk analysis.
    """
    try:
        # Generate unique filename if not provided
        if timestamp is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if output_path is None:
            output_path = f'static/report_{timestamp}.pdf'

        # Initialize canvas
        c = canvas.Canvas(output_path, pagesize=letter)
        width, height = letter
        margin = 50

        # Header Section
        c.setFont("Helvetica-Bold", 16)
        c.drawString(margin, height - margin, "Moon Boulder Detection Report")

        c.setFont("Helvetica", 10)
        c.drawString(margin, height - margin - 15, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # Add Divider Line
        c.setStrokeColorRGB(0.5, 0.5, 0.5)
        c.setLineWidth(0.5)
        c.line(margin, height - margin - 25, width - margin, height - margin - 25)

        # Add Boulder Stats
        y = height - margin - 50
        c.setFont("Helvetica-Bold", 12)
        c.drawString(margin, y, "Boulder Stats Summary:")
        y -= 15
        c.setFont("Helvetica", 10)

        stats_file = "static/stats_summary.txt"
        if os.path.exists(stats_file):
            with open(stats_file, "r", encoding="utf-8") as f:
                for line in f.readlines():
                    if y < margin + 50:  # Prevent overlapping footer
                        c.showPage()
                        y = height - margin - 50
                    # Replace invalid characters with safe placeholders
                    safe_line = line.strip().encode("utf-8", "replace").decode("utf-8")
                    c.drawString(margin, y, safe_line)
                    y -= 12
        else:
            c.drawString(margin, y, "Stats summary not found.")
            y -= 12

        # Add Images
        def draw_image(title, path, y_offset):
            c.setFont("Helvetica-Bold", 12)
            c.drawString(margin, y_offset, title)
            y_offset -= 15
            if os.path.exists(path):
                try:
                    img = ImageReader(path)
                    img_width, img_height = img.getSize()
                    aspect_ratio = img_height / img_width
                    scaled_width = width - 2 * margin
                    scaled_height = scaled_width * aspect_ratio
                    if y_offset - scaled_height < margin + 50:  # Prevent overlapping footer
                        c.showPage()
                        y_offset = height - margin - 50
                    c.drawImage(path, margin, y_offset - scaled_height, scaled_width, scaled_height)
                    y_offset -= scaled_height + 20
                except Exception as e:
                    safe_error = str(e).encode("utf-8", "replace").decode("utf-8")
                    c.drawString(margin, y_offset, f"Could not load image: {path} (Error: {safe_error})")
                    y_offset -= 15
            else:
                c.drawString(margin, y_offset, f"Image not found: {path}")
                y_offset -= 15
            return y_offset

        # Replace emojis with plain text equivalents
        y = draw_image("Detected Boulders", "static/boulders_detected.jpg", y)
        y = draw_image("Clustered Boulder Plot", "static/clustered_boulders_plot.jpg", y)
        y = draw_image("Risk Heatmap", "static/risk_heatmap.jpg", y)

        # Footer
        c.setFont("Helvetica-Italic", 8)
        c.drawString(margin, margin, "© 2025 Moon Boulder Detection Team. All rights reserved.")
        c.drawRightString(width - margin, margin, "Page 1")

        # Save PDF
        c.save()

        print(f" PDF Report saved to: {output_path}")
        return output_path  # Return the generated file path

    except Exception as e:
        # Handle encoding issues in error messages
        safe_error = str(e).encode("utf-8", "replace").decode("utf-8")
        print(f"[ERROR] Failed to generate PDF: {safe_error}")
        return None