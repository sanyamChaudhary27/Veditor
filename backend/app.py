from fastapi import FastAPI, UploadFile, File, Form, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
import uuid
import cv2
import base64
from video_processor import VideoProcessor
from datetime import datetime, timedelta

app = FastAPI()

# Task storage with timestamps
tasks = {}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(__file__)
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
# Set default to Downloads folder as requested
OUTPUT_DIR = r"C:\Users\HP\Downloads"
MODEL_PATH = os.path.join(BASE_DIR, "model", "rvm_mobilenetv3.pth")

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

processor = VideoProcessor(MODEL_PATH)

async def run_processing_task(task_id, video_path, output_path, bg_path, bg_color, blur_radius, lighting_strength):
    try:
        def progress_update(current, total):
            progress = int((current / total) * 100)
            tasks[task_id]["progress"] = progress
            print(f"Task {task_id} - Progress: {progress}% ({current}/{total})")
        
        print(f"Starting processing for task {task_id}")
        print(f"Output path: {output_path}")
        
        # Initial progress update
        tasks[task_id]["progress"] = 1
        print(f"Task {task_id} - Initial progress set to 1%")
        
        processor.process_video(
            video_path, output_path, 
            background_path=bg_path, 
            background_color=bg_color, 
            blur_radius=blur_radius, 
            lighting_strength=lighting_strength,
            progress_callback=progress_update
        )
        tasks[task_id]["status"] = "completed"
        tasks[task_id]["progress"] = 100
        tasks[task_id]["output_path"] = output_path
        tasks[task_id]["output_url"] = f"/download/{os.path.basename(output_path)}"
        print(f"Task {task_id} completed successfully.")
    except Exception as e:
        print(f"Task {task_id} failed: {str(e)}")
        import traceback
        traceback.print_exc()
        tasks[task_id]["status"] = "failed"
        tasks[task_id]["error"] = str(e)
    finally:
        if os.path.exists(video_path):
            os.remove(video_path)
        if bg_path and os.path.exists(bg_path):
            os.remove(bg_path)

@app.post("/remove-background")
async def remove_background(
    background_tasks: BackgroundTasks,
    video: UploadFile = File(...),
    background: UploadFile = File(None),
    color_r: int = Form(0),
    color_g: int = Form(255),
    color_b: int = Form(0),
    blur_radius: int = Form(0),
    lighting_strength: float = Form(0.0),
    output_dir: str = Form(None)
):
    try:
        task_id = str(uuid.uuid4())
        video_path = os.path.join(UPLOAD_DIR, f"{task_id}_{video.filename}")
        
        # Check if output file already exists with same settings
        final_output_dir = OUTPUT_DIR
        if output_dir and os.path.isdir(output_dir):
            final_output_dir = output_dir
        
        output_path = os.path.join(final_output_dir, f"out_{task_id}_{video.filename}")
        
        # Check if file already exists (skip reprocessing)
        if os.path.exists(output_path):
            print(f"Output file already exists: {output_path}")
            return {
                "task_id": task_id,
                "status": "completed",
                "output_url": f"/download/{os.path.basename(output_path)}",
                "cached": True
            }
        
        with open(video_path, "wb") as buffer:
            shutil.copyfileobj(video.file, buffer)

        bg_path = None
        if background:
            bg_path = os.path.join(UPLOAD_DIR, f"bg_{task_id}_{background.filename}")
            with open(bg_path, "wb") as buffer:
                shutil.copyfileobj(background.file, buffer)

        tasks[task_id] = {"status": "processing", "progress": 0, "created_at": datetime.now().isoformat()}
        
        background_tasks.add_task(
            run_processing_task, 
            task_id, video_path, output_path, bg_path, 
            (color_b, color_g, color_r), blur_radius, lighting_strength
        )

        return {"task_id": task_id}
    except Exception as e:
        print(f"Error in /remove-background: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/status/{task_id}")
async def get_status(task_id: str):
    if task_id not in tasks:
        # Return a default "not found" response that won't cause polling to fail
        return {
            "status": "not_found",
            "progress": 0,
            "error": "Task not found or expired"
        }
    task_data = tasks[task_id]
    print(f"Status request for {task_id}: progress={task_data.get('progress', 0)}%, status={task_data.get('status', 'unknown')}")
    return task_data

@app.post("/preview")
async def preview_frame(
    video: UploadFile = File(...),
    background: UploadFile = File(None),
    color_r: int = Form(0),
    color_g: int = Form(255),
    color_b: int = Form(0),
    blur_radius: int = Form(0),
    lighting_strength: float = Form(0.0)
):
    try:
        temp_id = str(uuid.uuid4())
        video_path = os.path.join(UPLOAD_DIR, f"temp_preview_{temp_id}_{video.filename}")
        
        with open(video_path, "wb") as buffer:
            shutil.copyfileobj(video.file, buffer)

        cap = cv2.VideoCapture(video_path)
        ret, frame = cap.read()
        cap.release()
        os.remove(video_path)

        if not ret:
            return JSONResponse(status_code=400, content={"error": "Could not read video"})

        bg_path = None
        if background:
            bg_path = os.path.join(UPLOAD_DIR, f"temp_bg_{temp_id}_{background.filename}")
            with open(bg_path, "wb") as buffer:
                shutil.copyfileobj(background.file, buffer)

        processed_frame = processor.process_single_frame(
            frame, bg_path, (color_b, color_g, color_r), blur_radius, lighting_strength
        )
        
        if bg_path and os.path.exists(bg_path):
            os.remove(bg_path)

        _, buffer = cv2.imencode('.jpg', processed_frame)
        img_str = base64.b64encode(buffer).decode('utf-8')
        
        return {"preview_url": f"data:image/jpeg;base64,{img_str}"}
    except Exception as e:
        print(f"Error in /preview: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/download/{filename}")
async def download_video(filename: str):
    file_path = os.path.join(OUTPUT_DIR, filename)
    if os.path.exists(file_path):
        return FileResponse(file_path)
    return JSONResponse(status_code=404, content={"error": "File not found"})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
