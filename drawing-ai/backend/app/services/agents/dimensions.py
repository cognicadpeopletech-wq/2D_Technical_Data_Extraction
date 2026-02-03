import math
import re
import logging
import numpy as np

class DimensionExtractionAgent:
    """
    The FEATURE CLASSIFICATION & LINKING Agent.
    """
    
    @staticmethod
    def classify_feature(text):
        """
        Classifies text string into feature semantic categories using Regex rules.
        """
        t = text.strip()
        
        # 1. BORES / HOLES
        if "Ø" in t or "THRU" in t.upper() or "DEPTH" in t.upper() or "M" in t and any(c.isdigit() for c in t):
            # M-threads (M8, M6x1)
            # But ensure it has digits.
            return "bores"
            
        # 2. CHAMFERS
        if "45°" in t or "CHAMFER" in t.upper():
            return "chamfers"
            
        # 3. RADII
        if re.match(r"^R\s*\d+", t, re.IGNORECASE):
            return "radii"
            
        # 4. GD&T
        if "|" in t or any(s in t.encode('utf-8', 'ignore').decode('utf-8') for s in ["⊥", "⌖", "∥", "⌯", "⏥", "⏶", "⌓"]):
             # Simple string check might fail with encoding, but robust enough for now
            return "gdts"
            
        # 5. DIMENSIONS
        if any(c.isdigit() for c in t):
            return "dimensions"
            
        # 6. NOTES
        return "notes"

    @staticmethod
    def is_inside(bbox, region_bbox):
        """
        Returns True if bbox is strictly inside region_bbox.
        bbox: [x, y, w, h]
        region_bbox: [rx, ry, rw, rh]
        """
        x, y, w, h = bbox
        rx, ry, rw, rh = region_bbox
        cx, cy = x + w/2, y + h/2
        
        return (cx > rx) and (cx < rx + rw) and (cy > ry) and (cy < ry + rh)

    @staticmethod
    def process(context):
        logging.info("[DimAgent] Starting Feature Classification & Linking (Werk24 Flow)...")
        
        arrows = [s for s in context["features"]["geometric_shapes"] if s["type"] == "arrow"]
        text_blocks = context.get("ocr_blocks", [])
        
        # Initialize Feature Buckets
        features = {
            "dimensions": [],
            "bores": [],
            "chamfers": [],
            "radii": [],
            "gdts": [],
            "notes": []
        }
        
        # Global Balloon ID Counter
        global_id_counter = 1
        
        img_h, img_w = context["original_image"].shape[:2]
        active_area = context["layout"].get("active_area")
        title_block = context["layout"].get("title_block")
        tables = context["layout"].get("tables", [])
        
        for txt in text_blocks:
            t_text = txt["text"]
            t_center = txt["center"]
            
            # --- STEP 1: FORBIDDEN ZONES CHECK ---
            # "Is text inside Title Block / Forbidden Zone? YES -> IGNORE"
            
            # 1. Title Block (STRICT)
            if title_block:
                if DimensionExtractionAgent.is_inside(txt["bbox"], title_block["bbox"]):
                     continue # Ignore metadata
            
            # 2. Tables Check
            in_table = False
            for tbl in tables:
                if DimensionExtractionAgent.is_inside(txt["bbox"], tbl["bbox"]):
                    in_table = True
                    break
            if in_table:
                continue

            # 3. Margin Check (Visual Border & Active Area)
            # Absolute edge guard for grid numbers
            edge_buffer = 65 
            w, h = img_w, img_h
            if (t_center[0] < edge_buffer) or (t_center[0] > w - edge_buffer) or \
               (t_center[1] < edge_buffer) or (t_center[1] > h - edge_buffer):
                 clean_txt = t_text.strip().upper()
                 if (len(clean_txt) <= 2 and clean_txt.isalnum()) or clean_txt in ["REV", "SHEET", "SCALE"]:
                     continue
            
            if active_area:
                ax, ay, aw, ah = active_area["bbox"]
                if (t_center[0] < ax) or (t_center[0] > ax + aw) or (t_center[1] < ay) or (t_center[1] > ay + ah):
                    continue 

            # --- STEP 2: REGEX CLASSIFICATION ---
            # "Regex classify text (Ø, R, ±, M, x, °)"
            category = DimensionExtractionAgent.classify_feature(t_text)
            
            # --- STEP 3: IS DIMENSION-LIKE? ---
            # "Is dimension-like text? NO -> Mark as note"
            # Our classify_feature handles this. If 'notes', it skips the arrow check below.
            
            if category == "notes":
                 # Just add to notes, maybe link to general geometry later
                 features["notes"].append({
                    "id": str(global_id_counter),
                    "type": "NOTE",
                    "value": t_text,
                    "location": {"x": int(t_center[0]), "y": int(t_center[1]), "bbox": txt["bbox"]},
                    "linked_arrows": []
                 })
                 global_id_counter += 1
                 continue

            # --- STEP 4: ARROW FINDING ---
            # "Find nearest arrowhead"
            linked_arrows_ids = []
            
            if category in ["dimensions", "bores", "chamfers", "radii", "gdts"]:
                nearest_arrows = sorted(arrows, key=lambda a: math.dist(a["center"], t_center))[:2]
                
                if nearest_arrows:
                    dist = math.dist(nearest_arrows[0]["center"], t_center)
                    MAX_DIST = 150 # Pixels
                    if len(t_text.strip()) <= 2: MAX_DIST = 60
                        
                    # "Arrow found?"
                    if dist <= MAX_DIST:
                        linked_arrows_ids = [a["id"] for a in nearest_arrows]
                    else:
                         # "Check alignment (arrow <-> text <-> geometry)"
                         if len(arrows) >= 2:
                            sorted_x = sorted(arrows, key=lambda a: a["center"][0])
                            tcx, tcy = t_center
                            
                            left_arrows = [a for a in sorted_x if a["center"][0] < tcx - 20]
                            right_arrows = [a for a in sorted_x if a["center"][0] > tcx + 20]
                            
                            if left_arrows and right_arrows:
                                l_arrow = min(left_arrows, key=lambda a: abs(a["center"][0] - tcx))
                                r_arrow = min(right_arrows, key=lambda a: abs(a["center"][0] - tcx))
                                
                                arrows_aligned = abs(l_arrow["center"][1] - r_arrow["center"][1]) < 30
                                text_near_line_y = (l_arrow["center"][1] - 60) < tcy < (l_arrow["center"][1] + 30)
                                
                                if arrows_aligned and text_near_line_y:
                                     linked_arrows_ids = [l_arrow["id"], r_arrow["id"]]
                                     logging.info(f"[DimAgent] Linked wide feature: {t_text}")

            # --- STEP 5: FINAL REJECTION ---
            # "Arrow found? NO -> REJECT (orphan text)"
            # "Valid geometric link?" (Implied by arrow presence for now in POC)
            
            if category in ["dimensions", "bores", "chamfers", "radii"]:
                if not linked_arrows_ids:
                    logging.info(f"[DimAgent] REJECTING unlinked orphan: {t_text} (Category: {category})")
                    continue 

            # ACCEPT & ASSIGN ID
            feature_obj = {
                "id": str(global_id_counter),
                "type": category.upper(), 
                "value": t_text,
                "label": t_text,
                "location": {
                    "x": int(t_center[0]),
                    "y": int(t_center[1]),
                    "bbox": txt["bbox"]
                },
                "linked_arrows": linked_arrows_ids
            }
            
            features[category].append(feature_obj)
            global_id_counter += 1

        # MERGE buckets
        for key, val in features.items():
            context["features"][key] = val
            
        logging.info(f"[DimAgent] Classification Complete. Dims: {len(features['dimensions'])}")
        return context
