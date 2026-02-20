# Veditor AI 🎥✨

Veditor AI is a high-performance AI-powered video background removal application. It allows users to remove video backgrounds without a green screen, replace them with solid colors or custom images, and apply cinematic effects like background blur and smart lighting matching—all in HD quality with audio preservation.

![Demo Placeholder](https://via.placeholder.com/800x450?text=Veditor+AI+Background+Removal+Demo)

## 🌟 Key Features

- **AI-Powered Background Removal**: Uses [Robust Video Matting (RVM)](https://github.com/PeterL1n/RobustVideoMatting) for pixel-perfect edge detection and temporal consistency.
- **Audio Preservation**: Automatically extracts, processes, and reattaches audio to maintain synchronized sound.
- **Asynchronous Processing**: Background tasks prevent browser timeouts and allow seamless UI interaction.
- **Real-Time Progress Tracking**: Live progress bar (0-100%) showing video processing status.
- **Instant Effect Preview**: Preview effects on a single frame before processing the full video.
- **Cinematic Effects**:
  - **Smart Lighting Match**: Uses Lab color space statistics to blend subjects naturally into new backgrounds.
  - **Background Blur**: Adjustable depth-of-field effect for professional cinematography.
- **HD Export**: High-quality video output with H.264 codec and audio re-encoding.
- **Auto-Save**: Processed videos automatically save to your Downloads folder.

## 🚀 Tech Stack

- **Frontend**: Next.js 16 (Turbopack), React 19, Tailwind CSS v4, Lucide React.
- **Backend**: FastAPI, PyTorch, OpenCV, NumPy, torchvision.
- **AI Model**: Robust Video Matting (MobileNetV3 backbone for speed).
- **Audio Processing**: FFmpeg for audio extraction and re-encoding.

## 🛠️ Installation & Setup

### Prerequisites

- Python 3.9+
- Node.js 20+
- FFmpeg (for audio support)
- (Optional) NVIDIA GPU with CUDA for faster processing.

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/Veditor.git
cd Veditor
```

### 2. Install FFmpeg

**Windows (Chocolatey):**
```powershell
choco install ffmpeg
```

**Windows (Manual):**
1. Download from https://ffmpeg.org/download.html
2. Extract to `C:\ffmpeg`
3. Add `C:\ffmpeg\bin` to your system PATH

**macOS:**
```bash
brew install ffmpeg
```

**Linux:**
```bash
sudo apt-get install ffmpeg
```

### 3. Backend Setup

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

### 4. Frontend Setup

```bash
cd ../frontend
npm install
```

## 🏃 Running the Application

### Start the Backend

```bash
cd backend
python app.py
```

Backend runs at `http://localhost:8000`

### Start the Frontend (in a new terminal)

```bash
cd frontend
npm run dev
```

Frontend runs at `http://localhost:3000`

## 📖 Usage Guide

1. **Upload Video**: Drag and drop your video file (MP4, MOV, AVI supported).
2. **Choose Background**: 
   - Select a solid color, or
   - Upload a custom background image
3. **Adjust Effects**:
   - **Background Blur**: 0-100% for depth-of-field effect
   - **Smart Lighting Match**: 0-100% to blend lighting naturally
4. **Preview**: Click "Preview Effect on Frame" to see results on the first frame instantly.
5. **Process**: Click "Process This Video" and monitor the progress bar.
6. **Download**: Once complete, click "Download HD Result" or find it in your Downloads folder.

## 🔬 Performance Optimizations

- **Batch Inference**: Processes 4 frames simultaneously for optimal GPU/CPU utilization.
- **Vectorized Operations**: NumPy-based background blending for high-speed compositing.
- **Lab Color Space**: Lighting matching preserves natural color while adjusting tone.
- **Codec Selection**: Automatic fallback between MJPEG, H.264, and other codecs for compatibility.

## 🐛 Known Issues & Workarounds

- **Terminal Errors During Processing**: Videos still process and save correctly despite console errors. This is a known issue with FFmpeg integration on Windows.
- **Audio Not Detected**: If your input video has no audio track, the output will also be audio-free (this is normal).
- **Slow Processing**: First run may be slower as the model loads. Subsequent runs are faster.

## 🚀 Future Roadmap

Veditor AI is evolving into a comprehensive **AI-powered video editor** with:

- **Auto-Editing Features**:
  - Scene detection and automatic cuts
  - Intelligent transitions between scenes
  - Auto-generated captions and subtitles
  - Music sync and beat detection
  
- **Advanced Effects**:
  - Green screen replacement with AI
  - Object removal and inpainting
  - Face enhancement and beauty filters
  - Dynamic background effects
  
- **Workflow Automation**:
  - Batch processing for multiple videos
  - Template-based editing
  - AI-powered color grading
  - Automatic video summarization
  
- **Collaboration Features**:
  - Cloud storage integration
  - Real-time collaboration
  - Version control for edits
  - Team project management

- **Export Options**:
  - Multi-format export (MP4, WebM, ProRes)
  - Platform-specific optimization (YouTube, TikTok, Instagram)
  - Adaptive bitrate streaming

## 📊 Performance Metrics

- **Processing Speed**: ~3-4 frames/second on CPU, ~10+ fps on NVIDIA GPU
- **Memory Usage**: ~2-3GB for typical 1080p video
- **Output Quality**: Full HD (1920x1080) with H.264 codec
- **Audio Sync**: Frame-perfect audio alignment

## 🤝 Contributing

Contributions are welcome! Areas for improvement:

- GPU optimization
- Additional AI models
- UI/UX enhancements
- Performance profiling
- Bug fixes

## 📄 License

MIT License - Copyright (c) 2026 Veditor AI.

---

_Built with ❤️ for creators. Transforming video editing with AI._
