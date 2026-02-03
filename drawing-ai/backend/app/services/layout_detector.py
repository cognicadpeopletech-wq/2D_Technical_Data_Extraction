from ultralytics import YOLO
import os

class LayoutDetector:
    def __init__(self, model_path="models/yolov8-layout.pt"):
        self.model_path = model_path
        if os.path.exists(model_path):
            self.model = YOLO(model_path)
            self.valid = True
        else:
            print(f"WARNING: Layout model not found at {model_path}. Running in mock mode.")
            self.model = None
            self.valid = False

    def detect(self, image_path):
        if not self.valid:
            # Mock return for POC if model missing
            # Classes: 0=main_view, 1=detail_view, 2=title_block, 3=revision_table
            # Return dummy structure that mimics YOLO result
            return [
                {
                    "class": 2, # title_block
                    "bbox": [1000, 1000, 2000, 1500], # x1, y1, x2, y2
                    "conf": 0.95
                },
                 {
                    "class": 0, # main_view
                    "bbox": [0, 0, 1000, 1000],
                    "conf": 0.99
                }
            ]
        
        results = self.model(image_path)
        # Parse results to JSON-friendly format
        detections = []
        for result in results:
            for box in result.boxes:
                detections.append({
                    "class": int(box.cls[0].item()),
                    "bbox": box.xyxy[0].tolist(),
                    "conf": float(box.conf[0].item())
                })
        return detections
