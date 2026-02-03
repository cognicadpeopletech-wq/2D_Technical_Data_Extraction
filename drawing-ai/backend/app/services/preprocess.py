import cv2
import numpy as np
import os
import pypdfium2 as pdfium

def preprocess_image(image_path: str) -> str:
    """
    Reads an image (or PDF), converts it to grayscale, and removes noise.
    Returns the path to the processed image.
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found at {image_path}")

    # Handle PDF input
    if image_path.lower().endswith(".pdf"):
        pdf = pdfium.PdfDocument(image_path)
        page = pdf[0] # Load first page
        bitmap = page.render(scale=2.0) # Render high-res
        pil_image = bitmap.to_pil()
        
        # Save temp image for OpenCV
        temp_img_path = image_path.replace(".pdf", ".png")
        pil_image.save(temp_img_path)
        img = cv2.imread(temp_img_path)
    else:
        img = cv2.imread(image_path)

    if img is None:
        raise ValueError("Could not read image")

    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Apply Gaussian Blur to remove noise
    blur = cv2.GaussianBlur(gray, (5, 5), 0)

    # Save processed image
    # Calculate absolute path for robustness
    # image_path is in /data/raw_drawings/...
    # we want /data/processed/...
    
    base_dir = os.path.dirname(os.path.dirname(image_path)) # data
    processed_dir = os.path.join(base_dir, "processed")
    os.makedirs(processed_dir, exist_ok=True)
    
    filename = os.path.basename(image_path)
    # Ensure extension is .png for processed file
    filename = os.path.splitext(filename)[0] + ".png"
    
    processed_path = os.path.join(processed_dir, f"processed_{filename}")
    
    cv2.imwrite(processed_path, blur)
    
    return processed_path
