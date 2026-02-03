import logging
import math

class RelationshipAgent:
    """
    Connects disjointed entities.
    Example: "3x Ø10" Note -> Linked to 3 specific Circle geometries.
    """
    @staticmethod
    def process(context):
        logging.info("[RelAgent] Mapping relationships...")
        
        dims = context["features"].get("dimensions", []) + \
               context["features"].get("bores", []) + \
               context["features"].get("radii", [])
        
        shapes = context["features"].get("geometric_shapes", [])
        circles = [s for s in shapes if s["type"] == "circle"]
        
        # 1. Link Radial/Diameter Dimensions to Circles
        for dim in dims:
            dim_type = dim.get("type", "").upper()
            if dim_type in ["DIAMETER", "RADIUS", "BORES", "RADII"]: 
                t_center = [dim["location"]["x"], dim["location"]["y"]]
    
                nearest_circle = sorted(circles, key=lambda c: math.dist(c["center"], t_center))[:1]
                
                if nearest_circle:
                    target = nearest_circle[0]
                    dist = math.dist(target["center"], t_center)
                    # Radius check: text is often outside, but arrow touches rim.
                    if abs(dist - target["radius"]) < 100 or dist < target["radius"] + 200:
                        dim["applies_to"] = target["id"]
                        
        # 2. Link GD&T to Parent Features (Vertical Stacking)
        gdts = context["features"].get("gdts", [])
        potential_parents = dims + context["features"].get("bores", []) + context["features"].get("radii", [])
        
        for gdt in gdts:
            g_center = [gdt["location"]["x"], gdt["location"]["y"]]
            
            # Find nearest dimension ABOVE the GD&T frame
            # Heuristic: Same X range (+/- 50px), Y is less than GDT Y (above) but close (within 100px)
            
            best_parent = None
            min_dist = 9999
            
            for parent in potential_parents:
                p_center = [parent["location"]["x"], parent["location"]["y"]]
                
                # Check Horizontal Alignment
                if abs(p_center[0] - g_center[0]) < 80:
                    # Check Vertical Alignment (Parent must be above)
                    y_diff = g_center[1] - p_center[1]
                    if 0 < y_diff < 150:
                        if y_diff < min_dist:
                            min_dist = y_diff
                            best_parent = parent
                            
            if best_parent:
                gdt["applies_to_feature"] = best_parent["id"]
                # Also link parent to GDT?
                if "related_gdts" not in best_parent:
                    best_parent["related_gdts"] = []
                best_parent["related_gdts"].append(gdt["id"])
                
        return context
