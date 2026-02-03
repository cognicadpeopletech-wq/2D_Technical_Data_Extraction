from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.pipeline import run_pipeline
import shutil
import os
import uuid

router = APIRouter(prefix="/extract", tags=["extract"])

@router.post("", summary="Upload and extract drawing data", include_in_schema=False)
@router.post("/", summary="Upload and extract drawing data")
async def extract_drawing(file: UploadFile = File(...)):
    try:
        # Save file
        file_ext = os.path.splitext(file.filename)[1]
        filename = f"{uuid.uuid4()}{file_ext}"
        
        # Calculate absolute path to data directory (assumed parallel to backend)
        # current file is in backend/app/api/
        # we want drawing-ai/data/raw_drawings
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) # drawing-ai/backend
        project_root = os.path.dirname(base_dir) # drawing-ai
        save_dir = os.path.join(project_root, "data", "raw_drawings")
        
        save_path = os.path.join(save_dir, filename)
        
        # Ensure dir exists
        os.makedirs(save_dir, exist_ok=True)
        
        with open(save_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Run pipeline
        result = await run_pipeline(save_path)
        
        return result
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
