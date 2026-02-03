def inside_bbox(inner_bbox, outer_bbox):
    """
    Check if inner_bbox is inside outer_bbox.
    bbox format: [x1, y1, x2, y2]
    """
    ix1, iy1, ix2, iy2 = inner_bbox
    ox1, oy1, ox2, oy2 = outer_bbox
    
    return ix1 >= ox1 and iy1 >= oy1 and ix2 <= ox2 and iy2 <= oy2

def apply_rules(detections, layout_results):
    """
    Filter detections based on layout rules (e.g., ignore title block).
    """
    title_block_bbox = None
    layout_bboxes = []
    
    # excessive safety check
    if isinstance(layout_results, list):
        for l in layout_results:
             if isinstance(l, dict) and l.get("class") == 2: # title_block class id
                 title_block_bbox = l.get("bbox")
                 break
    
    clean_detections = []
    for d in detections:
        # If we have a title block, and this detection is inside it, skip it
        if title_block_bbox and "bbox" in d:
             if inside_bbox(d["bbox"], title_block_bbox):
                 continue
        
        clean_detections.append(d)
        
    return clean_detections
