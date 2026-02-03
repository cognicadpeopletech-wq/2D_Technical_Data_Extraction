import cv2
import numpy as np
import logging

class GeometryAgent:
    """
    Detects geometric primitives: Lines, Circles, Arrows.
    This provides the "Anchor Points" for dimensions.
    """
    @staticmethod
    def process(context):
        logging.info("[GeometryAgent] Detecting shapes...")
        # img = context["original_image"]
        gray = context["processed_image"]
        edges = cv2.Canny(gray, 50, 150)
        
        shapes = []
        
        # 1. Circle Detection (Hough Transform)
        circles = cv2.HoughCircles(
            gray, cv2.HOUGH_GRADIENT, dp=1.2, minDist=30,
            param1=50, param2=30, minRadius=5, maxRadius=500
        )
        
        if circles is not None:
            circles = np.round(circles[0, :]).astype("int")
            for (x, y, r) in circles:
                shapes.append({
                    "id": f"circle_{len(shapes)}",
                    "type": "circle",
                    "center": [int(x), int(y)],
                    "radius": int(r),
                    "bbox": [int(x-r), int(y-r), int(x+r), int(y+r)]
                })
        
        # 2. Arrowhead Detection (Contour Analysis)
        # This is critical for dimensions.
        contours, _ = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        
        for cnt in contours:
            area = cv2.contourArea(cnt)
            # Filter for small shapes (arrowheads are usually small relative to drawing)
            if 10 < area < 500: 
                peri = cv2.arcLength(cnt, True)
                approx = cv2.approxPolyDP(cnt, 0.04 * peri, True)
                
                # Triangles have 3 vertices
                if len(approx) == 3:
                    # Potential arrowhead
                    # Compute centroid
                    M = cv2.moments(cnt)
                    if M["m00"] != 0:
                        cX = int(M["m10"] / M["m00"])
                        cY = int(M["m01"] / M["m00"])
                        shapes.append({
                            "id": f"arrow_{len(shapes)}",
                            "type": "arrow",
                            "center": [cX, cY],
                            "bbox": cv2.boundingRect(cnt)
                        })

        # 3. Line Detection
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=50, minLineLength=30, maxLineGap=10)
        if lines is not None:
             for line in lines:
                 x1, y1, x2, y2 = line[0]
                 shapes.append({
                     "id": f"line_{len(shapes)}",
                     "type": "line",
                     "start": [int(x1), int(y1)],
                     "end": [int(x2), int(y2)]
                 })

        context["features"]["geometric_shapes"] = shapes
        logging.info(f"[GeometryAgent] Detected {len(shapes)} geometric entities.")
        return context
