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

  const handleProcessVideo = async () => {
    if (!videoFile) return;

    setIsProcessing(true);
    setProcessedVideoUrl(null);

    const formData = new FormData();
    formData.append("video", videoFile);
    if (backgroundFile) {
      formData.append("background", backgroundFile);
    }
    formData.append("color_r", backgroundColor.r.toString());
    formData.append("color_g", backgroundColor.g.toString());
    formData.append("color_b", backgroundColor.b.toString());

    try {
      const response = await fetch("http://localhost:8000/remove-background", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) throw new Error("Processing failed");

      const data = await response.json();
      setProcessedVideoUrl(`http://localhost:8000${data.output_video_url}`);
    } catch (error) {
      console.error("Error:", error);
      alert("An error occurred during video processing.");
    } finally {
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
                  Processing HD Video...
                </>
              ) : (
                <>
                  Process Video
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
                <div className="absolute inset-0 bg-black/60 backdrop-blur-sm z-20 flex flex-col items-center justify-center rounded-xl border border-zinc-800">
                  <Loader2 className="w-12 h-12 text-blue-500 animate-spin mb-4" />
                  <p className="text-blue-400 font-medium animate-pulse">AI is predicting masks...</p>
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
                className="flex items-center justify-center gap-2 w-full py-3 bg-zinc-800 hover:bg-zinc-700 rounded-xl font-semibold transition-all"
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
