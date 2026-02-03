import logging
import os
from .drawing_analyst import DrawingAnalyst
from ..schemas.output_schema import DrawingOutput, Dimension

async def run_pipeline(file_path: str) -> DrawingOutput:
    logging.info(f"Using Advanced Multi-Agent Pipeline for {file_path}")
    
    # Run the new Analyst
    result = DrawingAnalyst.analyze(file_path)
    
    if not result.get("success"):
        raise ValueError(f"Analysis Failed: {result.get('message')}")
        
    data = result["data"]
    features = data["features"]
    
    # Flatten features into a list of Dimension objects for the Frontend
    # The frontend expects a list of Dimensions with 'type', 'value', 'tolerance', 'bbox'
    
    frontend_dimensions = []
    
    # Helper to map internal feature format to Pydantic Dimension Schema
    def map_to_dim(feat_list, type_override=None):
        for f in feat_list:
            frontend_dimensions.append(Dimension(
                value=f.get("value", ""),
                tolerance=f.get("tolerance", ""), # Not extracted by Regex currently, but placeholder
                type=type_override if type_override else f.get("type", "unknown").lower(),
                bbox=f["location"]["bbox"]
            ))

    map_to_dim(features.get("dimensions", []), "linear")
    map_to_dim(features.get("bores", []), "diameter")
    map_to_dim(features.get("chamfers", []), "chamfer")
    map_to_dim(features.get("radii", []), "radius")
    
    # Handle Image URL
    processed_image_path = data.get("processed_image_path")
    relative_path = None
    if processed_image_path:
        relative_path = f"/data/processed/{os.path.basename(processed_image_path)}"
        logging.info(f"DEBUG: Processed Image URL: {relative_path}")

    return DrawingOutput(
        part_name=data.get("part_number") or data.get("designation") or "Unknown Part",
        material=data.get("material") or "Unknown Material",
        dimensions=frontend_dimensions,
        original_file=os.path.basename(file_path),
        processed_image_url=relative_path
    )
