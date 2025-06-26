import cv2
import pandas as pd
import numpy as np
import os

def detect_boulders(image_path):
    """
    Detects boulders in an image, calculates their features, and saves the results.
    """
    # Step 1: Load the image
    img = cv2.imread(image_path)

    # Step 2: Ensure the image is in 3-channel format
    if img is None:
        raise ValueError("Image not found or unable to read.")
    if len(img.shape) < 3 or img.shape[2] == 1:
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

    # Step 3: Preprocessing (Grayscale and Blurring)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (11, 11), 0)

    # Step 4: Thresholding (Otsu's Method for Dynamic Thresholding)
    _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # Step 5: Contour Detection
    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # Step 6: Initialize Data Storage
    boulder_data = []

    # Step 7: Process Each Contour
    for contour in contours:
        area = cv2.contourArea(contour)
        if area < 10:  # Ignore small contours (noise)
            continue

        # Enclosing Circle and Features
        (x, y), radius = cv2.minEnclosingCircle(contour)
        if radius > 2:  # Filter based on minimum radius
            diameter = 2 * radius
            perimeter = cv2.arcLength(contour, True)
            circularity = (4 * np.pi * area) / (perimeter ** 2) if perimeter != 0 else 0

            # Bounding Box for Aspect Ratio
            x_min, y_min, width, height = cv2.boundingRect(contour)
            aspect_ratio = width / height if height != 0 else 1.0

            # Shape Classification
            if circularity > 0.85 and 0.9 < aspect_ratio < 1.1:
                shape = 'Round'
            elif aspect_ratio > 1.5 or aspect_ratio < 0.7:
                shape = 'Elongated'
            else:
                shape = 'Irregular'

            # Visualization (Draw Circle with Color)
            color = (0, 255, 0) if shape == 'Round' else (0, 165, 255) if shape == 'Elongated' else (0, 0, 255)
            cv2.circle(img, (int(x), int(y)), int(radius), color, 2)

            # Append Boulder Data
            boulder_data.append([
                int(x), int(y), round(diameter, 2),
                round(area, 2), round(perimeter, 2),
                round(circularity, 2), round(aspect_ratio, 2), shape
            ])

    # Step 8: Save Detected Image
    os.makedirs('static', exist_ok=True)
    detected_image_path = 'static/boulders_detected.jpg'
    cv2.imwrite(detected_image_path, img)
    print(f"[✅] Detected boulders image saved to: {detected_image_path}")

    # Step 9: Save Boulder Data to CSV
    output_csv = 'static/boulder_data.csv'
    df = pd.DataFrame(boulder_data, columns=[
        'X', 'Y', 'Diameter (m)', 'Area', 'Perimeter',
        'Circularity', 'AspectRatio', 'ShapeType'
    ])
    df.to_csv(output_csv, index=False)
    print(f"[✅] Boulder data saved to: {output_csv}")

    return output_csv
