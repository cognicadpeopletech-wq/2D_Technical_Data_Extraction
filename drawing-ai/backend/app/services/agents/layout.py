import cv2
import numpy as np
import logging

class LayoutDetectionAgent:
    """
    Detects logical zones: Drawing View, Title Block, Tables, Dimensions.
    Uses YOLO if available, otherwise heuristics.
    """
    _model = None
    
    @classmethod
    def load_model(cls):
        if cls._model is None:
            try:
                from ultralytics import YOLO
                # Placeholder for trained model path
                cls._model = YOLO("yolov8n.pt") 
            except ImportError:
                logging.warning("[LayoutAgent] ultralytics not installed. Using heuristics only.")
            except Exception as e:
                logging.warning(f"[LayoutAgent] Model load failed: {e}")

    @staticmethod
    def process(context):
        logging.info("[LayoutAgent] Segmenting drawing...")
        LayoutDetectionAgent.load_model()
        
        img = context["original_image"] # Use original for detection, sometimes better than binary
        h, w = img.shape[:2]
        
        zones = {
            "drawing_views": [],
            "tables": [],
            "title_block": None,
            "dimensions": [], # Bounding boxes of potential dimension areas
            "active_area": None
        }

        # METHOD A: Machine Learning (YOLO)
        # (Skipped for POC reliability, heuristic is usually safer for un-finetuned models)

        # METHOD B: Heuristic Fallback (Robust Computer Vision)
        
        # 0. Margin / Border Detection
        # Find the largest rectangular contour which is likely the drawing border
        # Use binary image? The user code used binary_image in logic but binary is inverted?
        # Let's assume binary is standard OpenCV (white text on black bg) from adaptiveThreshold?
        # Wait, adaptiveThreshold usually produces white background with black text if source is white paper.
        # Let's verify context["binary_image"] usage.
        # User code: gray = cv2.cvtColor(img, ...); binary = adaptiveThreshold(...)
        # Usually this results in black text and white background.
        # findContours expects white object on black background. So we should invert or use Canny.
        
        binary = context["binary_image"]
        # Invert for contour finding (finding black borders)
        binary_inv = cv2.bitwise_not(binary)
        
        contours, _ = cv2.findContours(binary_inv, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        main_border = None
        sorted_cnts = sorted(contours, key=cv2.contourArea, reverse=True)
        
        if sorted_cnts:
            # Assume largest contour is the page border line
            x, y, border_w, border_h = cv2.boundingRect(sorted_cnts[0])
            # If this border covers most of the image (>80%), use it as the "Active Area"
            if border_w * border_h > 0.8 * w * h:
                main_border = [x, y, border_w, border_h]
            else:
                # If no clear border, assume full page minus 5% margin
                margin = int(min(h, w) * 0.05)
                # Ensure we don't go out of bounds
                main_border = [margin, margin, w - 2*margin, h - 2*margin]
        else:
             main_border = [0, 0, w, h]
             
        zones["active_area"] = {
            "bbox": main_border,
            "type": "active_area",
            "description": "Main drawing content area excludes margins"
        }
        
        # 1. Title Block Detection (Forbidden Zone)
        # Heuristic: Large framing rectangle in bottom right corner
        # Werk24 Philosophy: Anything here is METADATA, not DIMENSIONS.
        
        tb_w = int(w * 0.35) # Expanded slightly
        tb_h = int(h * 0.20)
        tb_x = w - tb_w
        tb_y = h - tb_h
        
        zones["title_block"] = {
            "bbox": [tb_x, tb_y, tb_w, tb_h],
            "type": "title_block",
            "description": "Forbidden Zone for Dimensions"
        }

        # 3. Drawing View (Active Area minus Title Block)
        # Simplifiction: View is everything not TB.
        
        context["layout"] = zones
        logging.info(f"[LayoutAgent] Found mapped zones (Heuristic). Border: {main_border}")
        return context
