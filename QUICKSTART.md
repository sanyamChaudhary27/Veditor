# Veditor AI - Quick Start Guide 🚀

Get Veditor AI running in 5 minutes!

## Prerequisites

- Python 3.9+
- Node.js 20+
- FFmpeg (for audio)

## 1. Install FFmpeg (Windows)

```powershell
# Option A: Automatic (PowerShell as Admin)
$ProgressPreference = 'SilentlyContinue'
Invoke-WebRequest -Uri "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip" -OutFile "$env:TEMP\ffmpeg.zip"
Expand-Archive -Path "$env:TEMP\ffmpeg.zip" -DestinationPath "$env:TEMP\ffmpeg_extract"
Get-ChildItem "$env:TEMP\ffmpeg_extract" -Recurse -Filter "ffmpeg.exe" | Select-Object -First 1 | ForEach-Object { Copy-Item $_.Directory -Destination "C:\ffmpeg" -Recurse -Force }
[Environment]::SetEnvironmentVariable("Path", $env:Path + ";C:\ffmpeg\bin", "User")

# Option B: Manual
# 1. Download from https://ffmpeg.org/download.html
# 2. Extract to C:\ffmpeg
# 3. Add C:\ffmpeg\bin to PATH
```

**macOS:**
```bash
brew install ffmpeg
```

**Linux:**
```bash
sudo apt-get install ffmpeg
```

## 2. Clone Repository

```bash
git clone https://github.com/yourusername/Veditor.git
cd Veditor
```

## 3. Setup Backend

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Download AI model
python download_model.py
```

## 4. Setup Frontend

```bash
cd ../frontend
npm install
```

## 5. Run the App

**Terminal 1 - Backend:**
```bash
cd backend
python app.py
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

You should see:
```
▲ Next.js 16.0.0
- Local:        http://localhost:3000
```

## 6. Open in Browser

Go to: **http://localhost:3000**

## 7. Process Your First Video

1. **Upload Video**: Drag and drop an MP4/MOV file
2. **Choose Background**: Pick a color or upload an image
3. **Adjust Effects**: 
   - Background Blur: 0-100%
   - Smart Lighting: 0-100%
4. **Preview**: Click "Preview Effect on Frame"
5. **Process**: Click "Process This Video"
6. **Download**: Find your video in Downloads folder

## Troubleshooting

### Backend won't start
```bash
# Check if port 8000 is in use
netstat -ano | findstr :8000

# Kill the process (Windows)
taskkill /PID <PID> /F
```

### FFmpeg not found
```bash
# Verify installation
ffmpeg -version

# If not found, add to PATH manually
# Windows: System Properties → Environment Variables → Path → Add C:\ffmpeg\bin
```

### Frontend won't start
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
npm run dev
```

### Video processing fails
- Check console for error messages
- Ensure video format is supported (MP4, MOV, AVI)
- Try a smaller video file first
- Check available disk space

## Next Steps

- Read [README.md](README.md) for full documentation
- Check [ROADMAP.md](ROADMAP.md) for future features
- See [CONTRIBUTING.md](CONTRIBUTING.md) to contribute
- Join our community for support

## Performance Tips

- **First run**: Model loads, may take 30-60 seconds
- **GPU**: Install CUDA for 3-5x faster processing
- **Batch**: Process multiple videos for better efficiency
- **Resolution**: Lower resolution = faster processing

## Common Settings

### Professional Look
- Background Blur: 50-70%
- Smart Lighting: 30-50%

### Natural Look
- Background Blur: 20-40%
- Smart Lighting: 10-30%

### High Contrast
- Background Blur: 0-20%
- Smart Lighting: 70-100%

---

**Need help?** Check the [README.md](README.md) or open an issue on GitHub.

Happy editing! 🎬✨
