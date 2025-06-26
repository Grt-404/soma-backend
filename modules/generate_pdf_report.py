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
        
        # Always use the standard report.pdf name in static folder
        if output_path is None:
            output_path = 'static/report.pdf'
        
        # Remove old PDF if it exists
        if os.path.exists(output_path):
            os.remove(output_path)
            print(f"[🗑️] Removed old PDF: {output_path}")

        # Initialize canvas
        c = canvas.Canvas(output_path, pagesize=letter)
        width, height = letter
        margin = 50

        # Header Section
        c.setFont("Helvetica-Bold", 16)
        c.drawString(margin, height - margin, "SOMA - Moon Boulder Detection Report")

        c.setFont("Helvetica", 10)
        c.drawString(margin, height - margin - 15, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # Add Divider Line
        c.setStrokeColorRGB(0.5, 0.5, 0.5)
        c.setLineWidth(0.5)
        c.line(margin, height - margin - 25, width - margin, height - margin - 25)

        # Add Boulder Stats
        y = height - margin - 50
        c.setFont("Helvetica-Bold", 12)
        c.drawString(margin, y, "Boulder Analysis Summary:")
        y -= 20
        c.setFont("Helvetica", 10)

        # Load and display stats
        stats_file = "static/stats_summary.txt"
        if os.path.exists(stats_file):
            with open(stats_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
                for line in lines:
                    if y < margin + 100:  # Leave space for footer and next section
                        c.showPage()
                        y = height - margin - 50
                        c.setFont("Helvetica", 10)
                    
                    # Clean the line and handle special characters
                    clean_line = line.strip()
                    # Remove emoji characters for PDF compatibility
                    clean_line = ''.join(char for char in clean_line if ord(char) < 128)
                    
                    # Make headers bold
                    if clean_line.endswith('SUMMARY') or clean_line.endswith('DISTRIBUTION') or clean_line.endswith('COVERAGE'):
                        c.setFont("Helvetica-Bold", 10)
                    else:
                        c.setFont("Helvetica", 10)
                    
                    if clean_line and not clean_line.startswith('=') and not clean_line.startswith('-'):
                        c.drawString(margin, y, clean_line[:100])  # Limit line length
                        y -= 12
        else:
            c.drawString(margin, y, "Statistics summary not available.")
            y -= 15

        # Add Images Section
        def draw_image(title, path, y_offset):
            nonlocal c
            
            # Check if we need a new page
            if y_offset < margin + 200:
                c.showPage()
                y_offset = height - margin - 50
            
            c.setFont("Helvetica-Bold", 12)
            c.drawString(margin, y_offset, title)
            y_offset -= 20
            
            if os.path.exists(path):
                try:
                    img = ImageReader(path)
                    img_width, img_height = img.getSize()
                    
                    # Calculate scaled dimensions
                    max_width = width - 2 * margin
                    max_height = 150  # Fixed height for consistency
                    
                    aspect_ratio = img_width / img_height
                    if max_width / aspect_ratio <= max_height:
                        scaled_width = max_width
                        scaled_height = max_width / aspect_ratio
                    else:
                        scaled_height = max_height
                        scaled_width = max_height * aspect_ratio
                    
                    # Check if image fits on current page
                    if y_offset - scaled_height < margin + 50:
                        c.showPage()
                        y_offset = height - margin - 50
                        c.setFont("Helvetica-Bold", 12)
                        c.drawString(margin, y_offset, title)
                        y_offset -= 20
                    
                    c.drawImage(path, margin, y_offset - scaled_height, 
                              scaled_width, scaled_height)
                    y_offset -= scaled_height + 30
                    
                    print(f"[📷] Added image to PDF: {title}")
                    
                except Exception as e:
                    c.setFont("Helvetica", 9)
                    c.drawString(margin, y_offset, f"Could not load image: {os.path.basename(path)}")
                    y_offset -= 15
                    print(f"[⚠️] Could not add image {path}: {str(e)}")
            else:
                c.setFont("Helvetica", 9)
                c.drawString(margin, y_offset, f"Image not found: {os.path.basename(path)}")
                y_offset -= 15
                print(f"[⚠️] Image not found: {path}")
            
            return y_offset

        # Add analysis images
        y = draw_image("1. Original Image", "static/preview.jpg", y)
        y = draw_image("2. Detected Boulders", "static/boulders_detected.jpg", y)
        y = draw_image("3. Detected landslide", "static/landslides_detected.jpg", y)
        y = draw_image("4. Boulder Clustering Analysis", "static/clustered_boulders_plot.jpg", y)
        y = draw_image("5. Risk Assessment Heatmap", "static/risk_heatmap.jpg", y)
        y = draw_image("6. Source Point Analysis", "static/boulders_with_source.jpg", y)

        # Add final page with summary
        c.showPage()
        y = height - margin - 50
        
        c.setFont("Helvetica-Bold", 14)
        c.drawString(margin, y, "Analysis Complete")
        y -= 30
        
        c.setFont("Helvetica", 10)
        c.drawString(margin, y, "This report contains comprehensive analysis of lunar boulder distribution,")
        y -= 15
        c.drawString(margin, y, "clustering patterns, risk assessment, and source point estimation.")
        y -= 15
        c.drawString(margin, y, "All analysis performed using advanced computer vision and machine learning techniques.")

        # Footer on every page
        def add_footer(page_num):
            c.setFont("Helvetica-Oblique", 8)
            c.drawString(margin, margin - 10, "SOMA - Advanced Lunar Analysis System | Generated by Clueless Coders")
            c.drawRightString(width - margin, margin - 10, f"Page {page_num}")

        # Add footer to all pages (simple approach - just add to last page)
        add_footer(1)

        # Save PDF
        c.save()

        print(f"[✅] Fresh PDF report saved to: {output_path}")
        return output_path

    except Exception as e:
        print(f"[❌] Failed to generate PDF: {str(e)}")
        # Create a simple error PDF
        try:
            c = canvas.Canvas(output_path, pagesize=letter)
            c.setFont("Helvetica-Bold", 16)
            c.drawString(50, 750, "PDF Generation Error")
            c.setFont("Helvetica", 12)
            c.drawString(50, 720, f"Error: {str(e)}")
            c.drawString(50, 700, "Please try uploading your image again.")
            c.save()
            print(f"[📄] Error PDF created: {output_path}")
        except:
            pass
        return None