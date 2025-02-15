from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from test import is_plastic_garbage
from video import analyze_garbage_disposal
from fastapi import File, UploadFile, HTTPException
from pydantic import BaseModel
import base64
from typing import Optional
import io
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

class ImageRequest(BaseModel):
    image: str

@app.post("/detect")
async def detect_plastic(image_request: ImageRequest):
    try:
        logger.info("Received request")
        logger.info(f"Image data length: {len(image_request.image)}")
        
        if not image_request.image:
            raise HTTPException(status_code=400, detail="No image data provided")
            
        # Log the first few characters of the image data to verify format
        logger.info(f"Image data preview: {image_request.image[:50]}...")
        
        result = is_plastic_garbage(image_request.image)
        logger.info(f"Processing complete. Result: {result}")
        
        return {"plastic_garbage": "YES" if result else "NO"}
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/analyze")
async def video_analysis(video_url: str):
    try:
        result = analyze_garbage_disposal(video_url)
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)