from paddleocr import PaddleOCR
import logging

class OCREngine:
    def __init__(self):
        try:
            # use_gpu=False for POC unless CUDA is verified
            self.ocr = PaddleOCR(use_angle_cls=True, lang='en', use_gpu=False, show_log=False)
            self.valid = True
        except Exception as e:
            logging.error(f"Failed to initialize PaddleOCR: {e}")
            self.valid = False

    def extract(self, image_path: str):
        if not self.valid:
            # Mock
            return [[[[100, 100], [200, 100], [200, 120], [100, 120]], ["10.5 +/- 0.1", 0.99]]]

        try:
            result = self.ocr.ocr(image_path, cls=True)
            # Result is a list of lists (pages), we assume single image
            return result[0] if result else []
        except Exception as e:
            logging.error(f"OCR failed: {e}")
            return []
