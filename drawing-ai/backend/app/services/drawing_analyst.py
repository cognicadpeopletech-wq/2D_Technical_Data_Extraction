import logging
import cv2
import numpy as np
import json
from pathlib import Path
from .agents.preprocessing import PreprocessingAgent
from .agents.layout import LayoutDetectionAgent
from .agents.geometry import GeometryAgent
from .agents.dimensions import DimensionExtractionAgent
from .agents.text import TextTableAgent
from .agents.relationships import RelationshipAgent
from .agents.validation import ValidationAgent

from .agents.llm_validator import LLMValidatorAgent

class DrawingAnalyst:
    """
    The Conductor of the Drawing Analysis Orchestra.
    Sequentially calls agents to extract intelligence from the drawing.
    """
    
    @staticmethod
    def analyze(file_path: str):
        logging.info(f"[DrawingAnalyst] Starting analysis for: {file_path}")
        
        # 0. Initialize Context
        context = {
            "file_path": str(file_path),
            "original_image": None,
            "processed_image": None,
            "scale_ratio": 1.0, # px to mm ratio
            "drawing_metadata": {}, # Title block info
            "features": {
                "dimensions": [],
                "bores": [],
                "chamfers": [],
                "radii": [],
                "gdts": [],
                "notes": [],
                "geometric_shapes": [],
                "annotations": [],
                "tables": []
            },
            "logs": []
        }

        try:
            # 1. Preprocessing Agent
            context = PreprocessingAgent.process(context)
            if context.get("processed_image") is None:
                raise ValueError("Preprocessing failed to return an image.")

            # 2. Layout Detection Agent
            context = LayoutDetectionAgent.process(context)

            # 3. Geometry Understanding Agent
            context = GeometryAgent.process(context)

            # 4. Text & Table Extraction Agent
            context = TextTableAgent.process(context)

            # 5. Dimension Extraction Agent (CV Rules)
            context = DimensionExtractionAgent.process(context)
            
            # --- NEW STEP ---
            # 6. LLM Reasoning Agent (Validate & Normalize)
            context = LLMValidatorAgent.process(context)
            
            # 7. Relationship Mapping Agent
            context = RelationshipAgent.process(context)

            # 8. Validation Agent (Final Sanity)
            context = ValidationAgent.process(context)

            # 9. Final Formatting
            return DrawingAnalyst._format_output(context)

        except Exception as e:
            logging.error(f"[DrawingAnalyst] Analysis Critical Failure: {e}")
            import traceback
            traceback.print_exc()
            return {"success": False, "message": str(e)}

    @staticmethod
    def _format_output(context):
        # Convert internal context to frontend-friendly JSON
        
        def default_serializer(obj):
            if isinstance(obj, (np.int_, np.intc, np.intp, np.int8,
                                np.int16, np.int32, np.int64, np.uint8,
                                np.uint16, np.uint32, np.uint64)):
                return int(obj)
            elif isinstance(obj, (np.float_, np.float16, np.float32, 
                                  np.float64)):
                return float(obj)
            elif isinstance(obj, (np.ndarray,)): 
                return obj.tolist()
            return str(obj)

        data = {
            "designation": context["drawing_metadata"].get("title", "Unknown"),
            "part_number": context["drawing_metadata"].get("part_no", "Unknown"),
            "revision": context["drawing_metadata"].get("revision", "-"),
            "material": context["drawing_metadata"].get("material", "Unknown"),
            
            # Helper for legacy frontend compatibility (if needed) or simple access
            "processed_image_path": context.get("processed_image_path"),
            
            "features": {
                # New Segmented Structure matching Werk24 style
                "dimensions": context["features"].get("dimensions", []),
                "bores": context["features"].get("bores", []),
                "chamfers": context["features"].get("chamfers", []),
                "radii": context["features"].get("radii", []),
                "gdts": context["features"].get("gdts", []),
                "notes": context["features"].get("notes", []),
                
                # Metadata / Legacy
                "geometry": context["features"].get("geometric_shapes", []),
                "tables": context["features"].get("tables", [])
            }
        }
        
        return {
            "success": True, 
            "data": data,
            # "raw_context": json.loads(json.dumps(context, default=default_serializer, skipkeys=True)) 
        }
