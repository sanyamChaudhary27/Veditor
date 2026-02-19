"use client";

import { useState } from "react";
import FileUpload from "@/components/FileUpload";
import VideoPreview from "@/components/VideoPreview";
import BackgroundPicker from "@/components/BackgroundPicker";
import { Loader2, Sparkles, Download, ArrowRight } from "lucide-react";

export default function Home() {
  const [videoFile, setVideoFile] = useState<File | null>(null);
  const [backgroundFile, setBackgroundFile] = useState<File | null>(null);
  const [backgroundColor, setBackgroundColor] = useState({ r: 0, g: 255, b: 0 });
  const [isProcessing, setIsProcessing] = useState(false);
  const [processedVideoUrl, setProcessedVideoUrl] = useState<string | null>(null);
  const [blurRadius, setBlurRadius] = useState(0);
  const [lightingStrength, setLightingStrength] = useState(0);
  const [taskId, setTaskId] = useState<string | null>(null);
  const [progress, setProgress] = useState(0);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [isPreviewLoading, setIsPreviewLoading] = useState(false);

  const handlePreview = async () => {
    if (!videoFile) return;
    setIsPreviewLoading(true);
    
    const formData = new FormData();
    formData.append("video", videoFile);
    if (backgroundFile) {
      formData.append("background", backgroundFile);
    }
    formData.append("color_r", backgroundColor.r.toString());
    formData.append("color_g", backgroundColor.g.toString());
    formData.append("color_b", backgroundColor.b.toString());
    formData.append("blur_radius", blurRadius.toString());
    formData.append("lighting_strength", (lightingStrength / 100).toString());

    try {
      const response = await fetch("http://localhost:8000/preview", {
        method: "POST",
        body: formData,
      });
      const data = await response.json();
      setPreviewUrl(data.preview_url);
    } catch (error) {
      console.error("Preview error:", error);
    } finally {
      setIsPreviewLoading(false);
    }
  };

  const pollStatus = (id: string) => {
    const interval = setInterval(async () => {
      try {
        const response = await fetch(`http://localhost:8000/status/${id}`);
        if (!response.ok) return;
        
        const data = await response.json();
        setProgress(data.progress);
        
        if (data.status === "completed") {
          setProcessedVideoUrl(`http://localhost:8000${data.output_url}`);
          setIsProcessing(false);
          setTaskId(null);
          clearInterval(interval);
        } else if (data.status === "failed") {
          alert(`Processing failed: ${data.error}`);
          setIsProcessing(false);
          setTaskId(null);
          clearInterval(interval);
        }
      } catch (error) {
        console.error("Polling error:", error);
      }
    }, 1000);
  };

  const handleProcessVideo = async () => {
    if (!videoFile) return;

    setIsProcessing(true);
    setProgress(0);
    setProcessedVideoUrl(null);

    const formData = new FormData();
    formData.append("video", videoFile);
    if (backgroundFile) {
      formData.append("background", backgroundFile);
    }
    formData.append("color_r", backgroundColor.r.toString());
    formData.append("color_g", backgroundColor.g.toString());
    formData.append("color_b", backgroundColor.b.toString());
    formData.append("blur_radius", blurRadius.toString());
    formData.append("lighting_strength", (lightingStrength / 100).toString());

    try {
      const response = await fetch("http://localhost:8000/remove-background", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) throw new Error("Could not start processing");

      const data = await response.json();
      setTaskId(data.task_id);
      pollStatus(data.task_id);
    } catch (error) {
      console.error("Error:", error);
      alert("An error occurred while starting the video processing.");
      setIsProcessing(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#09090b] text-zinc-100 font-sans selection:bg-blue-500/30">
      {/* Background Glow */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-[25%] -left-[10%] w-[50%] h-[50%] bg-blue-600/10 blur-[120px] rounded-full" />
        <div className="absolute top-[20%] -right-[5%] w-[40%] h-[40%] bg-purple-600/10 blur-[120px] rounded-full" />
      </div>

      <div className="relative z-10 max-w-6xl mx-auto px-6 py-12">
        {/* Header */}
        <header className="flex items-center justify-between mb-16">
          <div className="flex items-center space-x-2">
            <div className="bg-blue-600 p-2 rounded-lg">
              <Sparkles className="w-6 h-6 text-white" />
            </div>
            <span className="text-xl font-bold tracking-tight">Veditor AI</span>
          </div>
          <nav className="hidden md:flex items-center space-x-8 text-sm font-medium text-zinc-400">
            <a href="#" className="hover:text-white transition-colors">Features</a>
            <a href="#" className="hover:text-white transition-colors">Pricing</a>
            <a href="#" className="hover:text-white transition-colors">API</a>
          </nav>
        </header>

        {/* Hero Section */}
        <div className="text-center mb-16">
          <h1 className="text-5xl md:text-6xl font-extrabold tracking-tight mb-6 bg-clip-text text-transparent bg-gradient-to-b from-white to-zinc-500">
            Remove Video Backgrounds <br /> with Cinematic Quality
          </h1>
          <p className="text-zinc-400 text-lg max-w-2xl mx-auto">
            Our AI-powered engine uses temporal consistency to give you pixel-perfect 
            background removal for HD videos. No green screen required.
          </p>
        </div>

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-start">
          {/* Controls Column */}
          <div className="space-y-8">
            <section className="space-y-4">
              <h2 className="text-lg font-semibold flex items-center gap-2">
                <span className="bg-blue-600/20 text-blue-400 w-6 h-6 rounded-full flex items-center justify-center text-xs">1</span>
                Upload Your Video
              </h2>
              <FileUpload
                label="Choose a video file"
                accept={{ "video/*": [".mp4", ".mov", ".avi"] }}
                onFileSelect={setVideoFile}
              />
            </section>

            <section className="space-y-4">
              <h2 className="text-lg font-semibold flex items-center gap-2">
                <span className="bg-blue-600/20 text-blue-400 w-6 h-6 rounded-full flex items-center justify-center text-xs">2</span>
                Choose New Background
              </h2>
              <BackgroundPicker
                onBackgroundSelect={setBackgroundFile}
                onColorSelect={setBackgroundColor}
              />
            </section>

            <section className="space-y-6 bg-zinc-900/50 p-6 rounded-2xl border border-zinc-800">
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <label className="text-sm font-medium text-zinc-400">Background Blur</label>
                  <span className="text-xs font-mono text-blue-400">{blurRadius}%</span>
                </div>
                <input
                  type="range"
                  min="0"
                  max="100"
                  value={blurRadius}
                  onChange={(e) => setBlurRadius(parseInt(e.target.value))}
                  className="w-full h-1.5 bg-zinc-800 rounded-lg appearance-none cursor-pointer accent-blue-600"
                />
              </div>

              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <label className="text-sm font-medium text-zinc-400">Smart Lighting Match</label>
                  <span className="text-xs font-mono text-blue-400">{lightingStrength}%</span>
                </div>
                <input
                  type="range"
                  min="0"
                  max="100"
                  value={lightingStrength}
                  onChange={(e) => setLightingStrength(parseInt(e.target.value))}
                  className="w-full h-1.5 bg-zinc-800 rounded-lg appearance-none cursor-pointer accent-blue-600"
                />
              </div>

              <button
                onClick={handlePreview}
                disabled={!videoFile || isProcessing || isPreviewLoading}
                className="w-full py-2 bg-zinc-800 hover:bg-zinc-700 disabled:opacity-50 text-sm font-medium rounded-lg transition-colors flex items-center justify-center gap-2"
              >
                {isPreviewLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Sparkles className="w-4 h-4 text-blue-400" />}
                Preview Effect on Frame
              </button>
            </section>

            <button
              onClick={handleProcessVideo}
              disabled={!videoFile || isProcessing}
              className={`w-full py-4 rounded-xl font-bold text-lg flex items-center justify-center gap-2 transition-all shadow-xl ${
                !videoFile || isProcessing
                  ? "bg-zinc-800 text-zinc-500 cursor-not-allowed"
                  : "bg-blue-600 hover:bg-blue-500 text-white shadow-blue-900/20 hover:scale-[1.02]"
              }`}
            >
              {isProcessing ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  Processing Video...
                </>
              ) : (
                <>
                  Process Full Video
                  <ArrowRight className="w-5 h-5" />
                </>
              )}
            </button>
          </div>

          {/* Preview Column */}
          <div className="space-y-8 lg:sticky lg:top-12">
            <VideoPreview
              title="Input Preview"
              videoFile={videoFile}
            />
            
            <div className="relative">
              {isProcessing && (
                <div className="absolute inset-0 bg-black/80 backdrop-blur-md z-20 flex flex-col items-center justify-center rounded-xl border border-zinc-800 p-8 text-center">
                  <Loader2 className="w-12 h-12 text-blue-500 animate-spin mb-6" />
                  <div className="w-full bg-zinc-800 h-2 rounded-full mb-4 overflow-hidden">
                    <div 
                      className="bg-blue-600 h-full transition-all duration-300 ease-out shadow-[0_0_12px_rgba(37,99,235,0.4)]"
                      style={{ width: `${progress}%` }}
                    />
                  </div>
                  <p className="text-xl font-bold text-white mb-2">{progress}%</p>
                  <p className="text-blue-400 font-medium text-sm tracking-wide">AI IS PREDICTING MASKS & COMPOSITING...</p>
                </div>
              )}
              
              {!isProcessing && !processedVideoUrl && previewUrl && (
                <div className="absolute inset-0 z-10 rounded-xl overflow-hidden border border-zinc-800 bg-black">
                  <img src={previewUrl} alt="Effect Preview" className="w-full h-full object-contain" />
                  <div className="absolute top-2 right-2 bg-blue-600/80 text-[10px] font-bold px-2 py-1 rounded text-white uppercase tracking-widest backdrop-blur-sm">
                    Frame Preview
                  </div>
                </div>
              )}

              <VideoPreview
                title="Result Preview"
                processedVideoUrl={processedVideoUrl}
              />
            </div>

            {processedVideoUrl && (
              <a
                href={processedVideoUrl}
                download
                className="flex items-center justify-center gap-2 w-full py-4 bg-zinc-100 hover:bg-white text-black rounded-xl font-bold transition-all shadow-xl shadow-white/5 active:scale-95"
              >
                <Download className="w-5 h-5" />
                Download HD Result
              </a>
            )}
          </div>
        </div>

        {/* Footer */}
        <footer className="mt-32 pt-12 border-t border-zinc-800 text-center text-zinc-500 text-sm">
          <p>&copy; 2026 Veditor AI. Powered by Robust Video Matting.</p>
        </footer>
      </div>
    </div>
  );
}
