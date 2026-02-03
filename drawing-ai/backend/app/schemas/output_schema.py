from pydantic import BaseModel
from typing import List, Optional, Any

class Dimension(BaseModel):
    value: str
    tolerance: Optional[str] = None
    type: Optional[str] = None # linear, radius, diameter
    confidence: Optional[float] = None
    bbox: Optional[List[float]] = None

class DrawingOutput(BaseModel):
    part_name: Optional[str] = ""
    material: Optional[str] = ""
    dimensions: List[Dimension] = []
    gdnt: List[Any] = []
    holes: List[Any] = []
    datums: List[Any] = []
    original_file: str
    processed_image_url: Optional[str] = None
