import cv2
import numpy as np
import logging
import os

class PreprocessingAgent:
    @staticmethod
    def process(context):
        logging.info("[PreprocessingAgent] Starting...")
        file_path = context["file_path"]
        
        # 1. Load Image
        # Handle PDF conversion
        img = None
        if file_path.lower().endswith(".pdf"):
            try:
                import fitz  # PyMuPDF
                doc = fitz.open(file_path)
                page = doc.load_page(0) # Analyze first page
                zoom = 2.0 # Higher resolution for OCR (approx 144 DPI if base is 72)
                mat = fitz.Matrix(zoom, zoom)
                pix = page.get_pixmap(matrix=mat)
                
                # Convert to numpy (OpenCV format)
                # pix.samples is bytes, shape (h, w, 3) usually RGB
                img_data = np.frombuffer(pix.samples, dtype=np.uint8)
                img = img_data.reshape(pix.h, pix.w, pix.n)
                
                if pix.n == 3: # RGB
                    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
                elif pix.n == 4: # RGBA
                    img = cv2.cvtColor(img, cv2.COLOR_RGBA2BGR)
                    
                logging.info(f"[PreprocessingAgent] Converted PDF page 1 to image: {img.shape}")
            except ImportError:
                raise ImportError("PyMuPDF (fitz) not installed. Please install 'pymupdf' to process PDFs.")
            except Exception as e:
                raise ValueError(f"PDF Conversion failed: {e}")
        else:
            img = cv2.imread(file_path)

        if img is None:
            raise ValueError(f"Could not read image: {file_path}")
            
        context["original_image"] = img

        # 2. Convert to Grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # 3. Adaptive Thresholding (Binarization)
        # Good for drawings with uneven lighting or shadows
        binary = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 11, 2
        )

        # 4. De-skewing (Tilt Correction)
        # Find all contours to estimate rotation
        # Invert for processing (white lines on black bg)
        binary_inv = cv2.bitwise_not(binary)
        
        angle = 0.0
        try:
            coords = np.column_stack(np.where(binary_inv > 0))
            # Require enough points
            if len(coords) > 100:
                angle = cv2.minAreaRect(coords)[-1]
                if angle < -45:
                    angle = -(90 + angle)
                else:
                    angle = -angle
                    
                # Only rotate if significant tilt
                if abs(angle) > 0.5:
                    logging.info(f"[PreprocessingAgent] Correcting skew: {angle:.2f} deg")
                    (h, w) = img.shape[:2]
                    center = (w // 2, h // 2)
                    M = cv2.getRotationMatrix2D(center, angle, 1.0)
                    img = cv2.warpAffine(img, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
                    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                    # Re-binarize after rotation
                    binary = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
                    # Update context images
                    context["original_image"] = img
        except Exception as e:
            logging.warning(f"[PreprocessingAgent] De-skew failed: {e}")

        # 5. Denoise
        # Remove small specks (salt-and-pepper)
        processed = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
        
        # Save processed image to disk for frontend display
        # Calculate consistent path
        # Assume context["file_path"] is like .../data/raw_drawings/guid.pdf
        # We save to .../data/processed/processed_guid.png
        
        filename = os.path.basename(file_path)
        base_name = os.path.splitext(filename)[0] + ".png"
        
        data_root = os.path.dirname(os.path.dirname(file_path)) # data or project root?
        # Actually file_path comes from Extract API which sets it to .../data/raw_drawings/filename
        # So dirname is raw_drawings, dirname(dirname) is data
        
        processed_dir = os.path.join(os.path.dirname(os.path.dirname(file_path)), "processed")
        os.makedirs(processed_dir, exist_ok=True)
        
        processed_save_path = os.path.join(processed_dir, f"processed_{base_name}")
        cv2.imwrite(processed_save_path, processed)
        
        # Store metadata
        context["processed_image"] = processed # Grayscale denoised
        context["binary_image"] = binary # Binary for shape operations
        context["processed_image_path"] = processed_save_path # For frontend URL generation later
        
        logging.info("[PreprocessingAgent] Complete.")
        return context
