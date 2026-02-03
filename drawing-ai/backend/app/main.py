from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import os

# Disable PaddleOCR model check to prevent startup hang
os.environ["PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK"] = "True"

from app.api.extract import router as extract_router

app = FastAPI(title="Drawing AI Backend", version="1.0.0")

@app.middleware("http")
async def log_requests(request: Request, call_next):
    print(f"DEBUG: Incoming Request: {request.method} {request.url.path}")
    response = await call_next(request)
    print(f"DEBUG: Response Status: {response.status_code}")
    return response

# CORS
origins = [
    "http://localhost:5173",
    "http://localhost:3000",
    "http://127.0.0.1:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5174"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi.staticfiles import StaticFiles

data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data")
print(f"DEBUG: Mounting StaticFiles from: {data_dir}")
app.mount("/data", StaticFiles(directory=data_dir), name="data")

app.include_router(extract_router)

@app.get("/")
def health_check():
    return {"status": "running", "service": "Drawing AI"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
