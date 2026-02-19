# Veditor AI 🎥✨

Veditor AI is a premium, high-performance video background removal application. It allows users to remove video backgrounds without a green screen, replace them with solid colors or custom images, and apply cinematic effects like background blur and smart lighting matching—all in HD quality.

![Demo Placeholder](https://via.placeholder.com/800x450?text=Veditor+AI+Background+Removal+Demo)

## 🌟 Key Features

- **AI-Powered Background Removal**: Uses [Robust Video Matting (RVM)](https://github.com/PeterL1n/RobustVideoMatting) for pixel-perfect edge detection and temporal consistency.
- **Asynchronous Processing**: Refactored backend handles video tasks in background threads to prevent browser timeouts.
- **Real-Time Progress Tracking**: Visual progress bar (0-100%) showing the status of your video render.
- **Instant Effect Preview**: Click "Preview Effect on Frame" to see your settings on a single frame instantly before processing the full video.
- **Cinematic Effects**:
  - **Smart Lighting Match**: Uses $l\alpha\beta$ color space statistics to blend the person naturally into the new background.
  - **Background Blur**: Adjustable depth-of-field effect for a professional look.
- **HD Export**: High-quality video writing using OpenCV with high bitrate support.

## 🚀 Tech Stack

- **Frontend**: Next.js 16 (Turbopack), React 19, Tailwind CSS v4, Lucide React.
- **Backend**: FastAPI, PyTorch, OpenCV, NumPy, torchvision.
- **AI Model**: Robust Video Matting (MobileNetV3 backbone for speed).

## 🛠️ Installation & Setup

### Prerequisites

- Python 3.9+
- Node.js 20+
- (Optional) NVIDIA GPU with CUDA for faster processing.

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/Veditor.git
cd Veditor
```

### 2. Backend Setup

```bash
cd backend
# Create a virtual environment
python -m venv venv
source venv/bin/activate # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Download pre-trained weights
python download_model.py
```

### 3. Frontend Setup

```bash
cd ../frontend
npm install
```

## 🏃 Driving the App

### Start the Backend

```bash
# From the backend directory
#PS C:\Users\HP\OneDrive\Veditor/backend>
python app.py
```

Backend will run at `http://localhost:8000`.

### Start the Frontend

```bash
# From the frontend directory
#PS C:\Users\HP\OneDrive\Veditor/frontend>
npm run dev
```

Frontend will run at `http://localhost:3000`.

## 📖 Usage Guide

1. **Upload**: Drag and drop your video file (MP4/MOV).
2. **Setup Background**: Choose a solid color or upload a custom background image.
3. **Adjust Effects**:
   - Use the **Background Blur** slider for depth.
   - Use **Smart Lighting Match** to blend colors.
4. **Preview**: Click "Preview Effect on Frame" to see the result instantly on the first frame.
5. **Process**: Click "Process Full Video" and watch the progress bar.
6. **Download**: Once finished, download your cinematic HD result!

## 🔬 Performance Optimizations

- **Batch Inference**: Processes 4 frames at once to maximize CPU/GPU utilization.
- **Vectorized Compositing**: Background blending is performed using high-speed NumPy operations.
- **Color Space Transformation**: Lighting matching is done in the $l\alpha\beta$ space to preserve lightness and only match color statistics.

## 📄 License

MIT License - Copyright (c) 2026 Veditor AI.

---

_Built with ❤️ for creators._
