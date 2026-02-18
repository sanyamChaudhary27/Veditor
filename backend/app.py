from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
import uuid
from video_processor import VideoProcessor

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
OUTPUT_DIR = "outputs"
MODEL_PATH = os.path.join("backend", "model", "rvm_mobilenetv3.pth")

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

processor = VideoProcessor(MODEL_PATH)

@app.post("/remove-background")
async def remove_background(
    video: UploadFile = File(...),
    background: UploadFile = File(None),
    color_r: int = Form(0),
    color_g: int = Form(255),
    color_b: int = Form(0)
):
    video_id = str(uuid.uuid4())
    video_path = os.path.join(UPLOAD_DIR, f"{video_id}_{video.filename}")
    output_path = os.path.join(OUTPUT_DIR, f"out_{video_id}_{video.filename}")
    
    with open(video_path, "wb") as buffer:
        shutil.copyfileobj(video.file, buffer)

    bg_path = None
    if background:
        bg_path = os.path.join(UPLOAD_DIR, f"bg_{video_id}_{background.filename}")
        with open(bg_path, "wb") as buffer:
            shutil.copyfileobj(background.file, buffer)

    # Process video
    processor.process_video(
        video_path, 
        output_path, 
        background_path=bg_path, 
        background_color=(color_b, color_g, color_r)
    )

    return {"output_video_url": f"/download/{os.path.basename(output_path)}"}

@app.get("/download/{filename}")
async def download_video(filename: str):
    file_path = os.path.join(OUTPUT_DIR, filename)
    return FileResponse(file_path)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
