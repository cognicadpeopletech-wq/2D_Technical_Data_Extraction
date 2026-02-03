import logging
import re
import cv2
import numpy as np

try:
    from paddleocr import PaddleOCR
    PADDLE_AVAILABLE = True
except ImportError:
    PADDLE_AVAILABLE = False
    
try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False

class TextTableAgent:
    """
    Extracts text and tables using the best available OCR engine.
    Also handles Title Block parsing.
    """
    _ocr_engine = None

    @classmethod
    def get_engine(cls):
        if cls._ocr_engine is None and PADDLE_AVAILABLE:
            logging.info("[TextAgent] Loading PaddleOCR...")
            cls._ocr_engine = PaddleOCR(use_angle_cls=True, lang='en')
        return cls._ocr_engine

    @staticmethod
    def process(context):
        logging.info("[TextAgent] Extracting text...")
        img = context["original_image"]
        
        extracted_text_blocks = [] # List of {"bbox": [x,y,w,h], "text": "str"}
        
        engine = TextTableAgent.get_engine()
        
        if engine:
            # PaddleOCR returns [[[coords], (text, conf)], ...]
            results = engine.ocr(img)
            if results and results[0]:
                for line in results[0]:
                    coords = line[0] # [[x1,y1], [x2,y1], [x2,y2], [x1,y2]]
                    text, conf = line[1]
                    
                    # Compute bbox
                    xs = [pt[0] for pt in coords]
                    ys = [pt[1] for pt in coords]
                    x, y = min(xs), min(ys)
                    w, h = max(xs)-x, max(ys)-y
                    
                    extracted_text_blocks.append({
                        "bbox": [int(x), int(y), int(w), int(h)],
                        "text": text,
                        "conf": conf,
                        "center": [int(x + w/2), int(y + h/2)]
                    })
        elif TESSERACT_AVAILABLE:
            # Fallback to Tesseract
            data = pytesseract.image_to_data(img, config='--psm 11', output_type=pytesseract.Output.DICT)
            n_boxes = len(data['text'])
            for i in range(n_boxes):
                if int(data['conf'][i]) > 40 and data['text'][i].strip():
                    (x, y, w, h) = (data['left'][i], data['top'][i], data['width'][i], data['height'][i])
                    extracted_text_blocks.append({
                        "bbox": [x, y, w, h],
                        "text": data['text'][i],
                        "conf": float(data['conf'][i]) / 100.0,
                        "center": [x + w/2, y + h/2]
                    })
        else:
             logging.warning("[TextAgent] No OCR library found (PaddleOCR or Tesseract).")

        # 2. Parse Title Block (Heuristic)
        # Find text blocks inside the "title_block" zone found by LayoutAgent.
        tb_zone = context.get("layout", {}).get("title_block")
        
        if tb_zone:
            tx, ty, tw, th = tb_zone["bbox"]
            tb_texts = []
            for block in extracted_text_blocks:
                bx, by, bw, bh = block["bbox"]
                # Check intersection/containment
                # Center point is easiest check
                cx, cy = block["center"]
                if tx < cx < tx + tw and ty < cy < ty + th:
                    tb_texts.append(block["text"])
            
            # Simple Join for metadata extraction
            full_tb_text = " ".join(tb_texts)
            # Use Regex to extract specific fields
            TextTableAgent._extract_metadata(full_tb_text, context)
            
        context["ocr_blocks"] = extracted_text_blocks
        logging.info(f"[TextAgent] Extracted {len(extracted_text_blocks)} text blocks.")
        return context

    @staticmethod
    def _extract_metadata(text, context):
        def find_val(patterns, txt):
            for p in patterns:
                m = re.search(p, txt, re.IGNORECASE)
                if m: return m.group(1).strip()
            return None

        context["drawing_metadata"]["title"] = find_val([r"TITLE:\s*(.*?)(?:\s+|$)", r"DWG TITLE:\s*(.*?)"], text)
        context["drawing_metadata"]["part_no"] = find_val([r"PART NO:\s*(.*?)(?:\s+|$)", r"DWG NO:\s*(.*?)"], text)
        context["drawing_metadata"]["material"] = find_val([r"MATERIAL:\s*(.*?)(?:\s+|$)", r"MATL:\s*(.*?)"], text)
        context["drawing_metadata"]["revision"] = find_val([r"REV:\s*(.*?)(?:\s+|$)", r"REVISION:\s*(.*?)"], text)
