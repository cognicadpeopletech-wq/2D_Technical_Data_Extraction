from ultralytics import YOLO
import os

class SymbolDetector:
    def __init__(self, model_path="models/yolov8-symbols.pt"):
        self.model_path = model_path
        if os.path.exists(model_path):
            self.model = YOLO(model_path)
            self.valid = True
        else:
            print(f"WARNING: Symbol model not found at {model_path}. Running in mock mode.")
            self.model = None
            self.valid = False

    def detect(self, image_path):
        if not self.valid:
            # Mock return
            # Symbols: diameter, radius, etc.
            return [
                {
                    "class": "diameter",
                    "bbox": [500, 500, 520, 520],
                    "conf": 0.8
                }
            ]
        
        results = self.model(image_path)
        detections = []
        for result in results:
             for box in result.boxes:
                detections.append({
                    "class": int(box.cls[0].item()), # Or use names if available
                    "bbox": box.xyxy[0].tolist(),
                    "conf": float(box.conf[0].item())
                })
        return detections
