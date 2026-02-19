"use client";

import { useState } from "react";
import FileUpload from "@/components/FileUpload";
import VideoPreview from "@/components/VideoPreview";
import BackgroundPicker from "@/components/BackgroundPicker";
import { Loader2, Sparkles, Download, ArrowRight } from "lucide-react";

interface VideoItem {
  id: string;
  file: File;
  backgroundFile: File | null;
  backgroundColor: { r: number; g: number; b: number };
  blurRadius: number;
  lightingStrength: number;
  isProcessing: boolean;
  progress: number;
  taskId: string | null;
  processedVideoUrl: string | null;
  previewUrl: string | null;
  isPreviewLoading: boolean;
  error: string | null;
}

export default function Home() {
  const [videoList, setVideoList] = useState<VideoItem[]>([]);
  const [activeVideoId, setActiveVideoId] = useState<string | null>(null);
  const [outputDir, setOutputDir] = useState("");

  const activeVideo = videoList.find((v) => v.id === activeVideoId) || null;

  const updateActiveVideo = (updates: Partial<VideoItem>) => {
    if (!activeVideoId) return;
    setVideoList((prev) =>
      prev.map((v) => (v.id === activeVideoId ? { ...v, ...updates } : v))
    );
  };

  const handleFilesSelect = (files: File[]) => {
    const newVideos: VideoItem[] = files.map(file => ({
      id: Math.random().toString(36).substring(7),
      file,
      backgroundFile: null,
      backgroundColor: { r: 0, g: 255, b: 0 },
      blurRadius: 0,
      lightingStrength: 0,
      isProcessing: false,
      progress: 0,
      taskId: null,
      processedVideoUrl: null,
      previewUrl: null,
      isPreviewLoading: false,
      error: null,
    }));
    setVideoList((prev) => [...prev, ...newVideos]);
    if (newVideos.length > 0) {
      setActiveVideoId(newVideos[0].id);
    }
  };

  const handleProcessAll = async () => {
    const idleVideos = videoList.filter(v => !v.isProcessing && !v.processedVideoUrl);
    for (const video of idleVideos) {
      handleProcessVideo(video.id);
    }
  };

  const pollStatus = (id: string, taskId: string) => {
    const interval = setInterval(async () => {
      try {
        const response = await fetch(`http://localhost:8000/status/${taskId}`);
        if (!response.ok) return;
        
        const data = await response.json();
        
        setVideoList((prev) =>
          prev.map((v) =>
            v.id === id ? { ...v, progress: data.progress } : v
          )
        );
        
        if (data.status === "completed") {
          setVideoList((prev) =>
            prev.map((v) =>
              v.id === id ? { 
                ...v, 
                processedVideoUrl: `http://localhost:8000${data.output_url}`,
                isProcessing: false,
                taskId: null
              } : v
            )
          );
          clearInterval(interval);
        } else if (data.status === "failed") {
          setVideoList((prev) =>
            prev.map((v) =>
              v.id === id ? { 
                ...v, 
                error: data.error,
                isProcessing: false,
                taskId: null
              } : v
            )
          );
          clearInterval(interval);
        }
      } catch (error) {
        console.error("Polling error:", error);
      }
    }, 1000);
  };

  const handlePreview = async () => {
    if (!activeVideo) return;
    
    updateActiveVideo({ isPreviewLoading: true, processedVideoUrl: null });
    
    const formData = new FormData();
    formData.append("video", activeVideo.file);
    if (activeVideo.backgroundFile) {
      formData.append("background", activeVideo.backgroundFile);
    }
    formData.append("color_r", activeVideo.backgroundColor.r.toString());
    formData.append("color_g", activeVideo.backgroundColor.g.toString());
    formData.append("color_b", activeVideo.backgroundColor.b.toString());
    formData.append("blur_radius", activeVideo.blurRadius.toString());
    formData.append("lighting_strength", (activeVideo.lightingStrength / 100).toString());

    try {
      const response = await fetch("http://localhost:8000/preview", {
        method: "POST",
        body: formData,
      });
      if (!response.ok) {
        const errData = await response.json();
        throw new Error(errData.detail || "Preview failed");
      }
      const data = await response.json();
      updateActiveVideo({ previewUrl: data.preview_url, isPreviewLoading: false });
    } catch (error: any) {
      console.error("Preview error:", error);
      alert(`Preview failed: ${error.message}`);
      updateActiveVideo({ isPreviewLoading: false });
    }
  };

  const handleProcessVideo = async (videoId?: string) => {
    const id = videoId || activeVideoId;
    const target = videoList.find(v => v.id === id);
    if (!target || !id) return;

    setVideoList((prev) =>
      prev.map((v) =>
        v.id === id ? { ...v, isProcessing: true, progress: 0, processedVideoUrl: null } : v
      )
    );

    const formData = new FormData();
    formData.append("video", target.file);
    if (target.backgroundFile) {
      formData.append("background", target.backgroundFile);
    }
    formData.append("color_r", target.backgroundColor.r.toString());
    formData.append("color_g", target.backgroundColor.g.toString());
    formData.append("color_b", target.backgroundColor.b.toString());
    formData.append("blur_radius", target.blurRadius.toString());
    formData.append("lighting_strength", (target.lightingStrength / 100).toString());
    if (outputDir) {
      formData.append("output_dir", outputDir);
    }

    try {
      const response = await fetch("http://localhost:8000/remove-background", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) throw new Error("Could not start processing");

      const data = await response.json();
      setVideoList((prev) =>
        prev.map((v) =>
          v.id === id ? { ...v, taskId: data.task_id } : v
        )
      );
      pollStatus(id, data.task_id);
    } catch (error) {
      console.error("Error:", error);
      setVideoList((prev) =>
        prev.map((v) =>
          v.id === id ? { ...v, isProcessing: false, error: "Initialization failed" } : v
        )
      );
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
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-start">
          {/* Left Column: Video Queue & Selection */}
          <div className="lg:col-span-3 space-y-6">
            <section className="space-y-4">
              <h2 className="text-lg font-semibold flex items-center gap-2">
                <Sparkles className="w-5 h-5 text-blue-400" />
                Video Queue
              </h2>
              
              <div className="space-y-3">
                {videoList.map((video) => (
                  <button
                    key={video.id}
                    onClick={() => setActiveVideoId(video.id)}
                    className={`w-full p-3 rounded-xl border transition-all text-left flex items-center gap-3 ${
                      activeVideoId === video.id
                        ? "bg-blue-600/10 border-blue-600 shadow-[0_0_15px_rgba(37,99,235,0.1)]"
                        : "bg-zinc-900 border-zinc-800 border-transparent hover:border-zinc-700 hover:bg-zinc-900/80"
                    }`}
                  >
                    <div className="relative w-12 h-12 bg-zinc-950 rounded-lg overflow-hidden flex-shrink-0 border border-zinc-800">
                      {video.previewUrl ? (
                        <img src={video.previewUrl} className="w-full h-full object-cover" />
                      ) : (
                        <div className="w-full h-full flex items-center justify-center">
                          <Sparkles className="w-4 h-4 text-zinc-700" />
                        </div>
                      )}
                      {video.isProcessing && (
                        <div className="absolute inset-0 bg-blue-600/20 flex items-center justify-center">
                          <Loader2 className="w-4 h-4 text-blue-400 animate-spin" />
                        </div>
                      )}
                    </div>
                    <div className="min-w-0">
                      <p className="text-sm font-medium text-zinc-100 truncate">
                        {video.file.name}
                      </p>
                      <p className="text-[10px] text-zinc-500 uppercase tracking-wider font-bold">
                        {video.isProcessing ? `Processing ${video.progress}%` : video.processedVideoUrl ? "Completed" : "Idle"}
                      </p>
                    </div>
                  </button>
                ))}

                <FileUpload
                  label="Add more videos"
                  accept={{ "video/*": [".mp4", ".mov", ".avi"] }}
                  onFilesSelect={handleFilesSelect}
                />

                {videoList.length > 1 && (
                  <button
                    onClick={handleProcessAll}
                    className="w-full py-3 bg-zinc-800 hover:bg-zinc-700 text-zinc-300 text-sm font-bold rounded-xl transition-all border border-zinc-700 flex items-center justify-center gap-2"
                  >
                    <Sparkles className="w-4 h-4 text-blue-400" />
                    Process All Idle Videos
                  </button>
                )}
              </div>
            </section>
          </div>

          {/* Center Column: Controls */}
          <div className="lg:col-span-4 space-y-8">
            {!activeVideo ? (
              <div className="bg-zinc-900/50 p-12 rounded-2xl border border-zinc-800 text-center space-y-4">
                <div className="w-16 h-16 bg-zinc-800 rounded-full flex items-center justify-center mx-auto">
                  <ArrowRight className="w-8 h-8 text-zinc-600" />
                </div>
                <p className="text-zinc-500">Select or upload a video to start editing</p>
              </div>
            ) : (
              <>
                <section className="space-y-4">
                  <h2 className="text-lg font-semibold flex items-center gap-2">
                    <span className="bg-blue-600/20 text-blue-400 w-6 h-6 rounded-full flex items-center justify-center text-xs">1</span>
                    Choose New Background
                  </h2>
                  <BackgroundPicker
                    onBackgroundSelect={(file) => updateActiveVideo({ backgroundFile: file })}
                    onColorSelect={(color) => updateActiveVideo({ backgroundColor: color })}
                  />
                </section>

                <section className="space-y-6 bg-zinc-900/50 p-6 rounded-2xl border border-zinc-800">
                  <div className="space-y-4">
                    <div className="flex justify-between items-center">
                      <label className="text-sm font-medium text-zinc-400">Background Blur</label>
                      <span className="text-xs font-mono text-blue-400">{activeVideo.blurRadius}%</span>
                    </div>
                    <input
                      type="range"
                      min="0"
                      max="100"
                      value={activeVideo.blurRadius}
                      onChange={(e) => updateActiveVideo({ blurRadius: parseInt(e.target.value) })}
                      className="w-full h-1.5 bg-zinc-800 rounded-lg appearance-none cursor-pointer accent-blue-600"
                    />
                  </div>

                  <div className="space-y-4">
                    <div className="flex justify-between items-center">
                      <label className="text-sm font-medium text-zinc-400">Smart Lighting Match</label>
                      <span className="text-xs font-mono text-blue-400">{activeVideo.lightingStrength}%</span>
                    </div>
                    <input
                      type="range"
                      min="0"
                      max="100"
                      value={activeVideo.lightingStrength}
                      onChange={(e) => updateActiveVideo({ lightingStrength: parseInt(e.target.value) })}
                      className="w-full h-1.5 bg-zinc-800 rounded-lg appearance-none cursor-pointer accent-blue-600"
                    />
                  </div>

                  <button
                    onClick={handlePreview}
                    disabled={activeVideo.isProcessing || activeVideo.isPreviewLoading}
                    className="w-full py-2 bg-zinc-800 hover:bg-zinc-700 disabled:opacity-50 text-sm font-medium rounded-lg transition-colors flex items-center justify-center gap-2"
                  >
                    {activeVideo.isPreviewLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Sparkles className="w-4 h-4 text-blue-400" />}
                    Preview Effect on Frame
                  </button>
                </section>

                <section className="space-y-4 bg-zinc-900/50 p-6 rounded-2xl border border-zinc-800">
                  <h3 className="text-sm font-semibold text-zinc-400 uppercase tracking-wider">Save Settings</h3>
                  <div className="space-y-2">
                    <label className="text-xs text-zinc-500">Output Directory (Local Path)</label>
                    <input
                      type="text"
                      placeholder="C:\Users\...\Desktop (Optional)"
                      value={outputDir}
                      onChange={(e) => setOutputDir(e.target.value)}
                      className="w-full bg-zinc-950 border border-zinc-800 rounded-lg px-4 py-2 text-sm focus:outline-none focus:border-blue-500 transition-colors"
                    />
                  </div>
                </section>

                <button
                  onClick={() => handleProcessVideo()}
                  disabled={activeVideo.isProcessing}
                  className={`w-full py-4 rounded-xl font-bold text-lg flex items-center justify-center gap-2 transition-all shadow-xl ${
                    activeVideo.isProcessing
                      ? "bg-zinc-800 text-zinc-500 cursor-not-allowed"
                      : "bg-blue-600 hover:bg-blue-500 text-white shadow-blue-900/20 hover:scale-[1.02]"
                  }`}
                >
                  {activeVideo.isProcessing ? (
                    <>
                      <Loader2 className="w-5 h-5 animate-spin" />
                      Processing Video...
                    </>
                  ) : (
                    <>
                      Process This Video
                      <ArrowRight className="w-5 h-5" />
                    </>
                  )}
                </button>
              </>
            )}
          </div>

          {/* Right Column: Preview */}
          <div className="lg:col-span-5 space-y-8 lg:sticky lg:top-12">
            {activeVideo && (
              <>
                <VideoPreview
                  title="Source Video"
                  videoFile={activeVideo.file}
                />
                
                <div className="relative">
                  {activeVideo.isProcessing && (
                    <div className="absolute inset-0 bg-black/80 backdrop-blur-md z-20 flex flex-col items-center justify-center rounded-xl border border-zinc-800 p-8 text-center">
                      <Loader2 className="w-12 h-12 text-blue-500 animate-spin mb-6" />
                      <div className="w-full bg-zinc-800 h-2 rounded-full mb-4 overflow-hidden">
                        <div 
                          className="bg-blue-600 h-full transition-all duration-300 ease-out shadow-[0_0_12px_rgba(37,99,235,0.4)]"
                          style={{ width: `${activeVideo.progress}%` }}
                        />
                      </div>
                      <p className="text-xl font-bold text-white mb-2">{activeVideo.progress}%</p>
                      <p className="text-blue-400 font-medium text-sm tracking-wide uppercase">AI Matting in progress...</p>
                    </div>
                  )}
                  
                  {!activeVideo.isProcessing && !activeVideo.processedVideoUrl && activeVideo.previewUrl && (
                    <div className="absolute inset-0 z-10 rounded-xl overflow-hidden border border-zinc-800 bg-black">
                      <img src={activeVideo.previewUrl} alt="Effect Preview" className="w-full h-full object-contain" />
                      <div className="absolute top-2 right-2 bg-blue-600/80 text-[10px] font-bold px-2 py-1 rounded text-white uppercase tracking-widest backdrop-blur-sm">
                        Frame Preview
                      </div>
                    </div>
                  )}

                  <VideoPreview
                    title="Result Preview"
                    processedVideoUrl={activeVideo.processedVideoUrl}
                  />
                </div>

                {activeVideo.processedVideoUrl && (
                  <a
                    href={activeVideo.processedVideoUrl}
                    download
                    className="flex items-center justify-center gap-2 w-full py-4 bg-zinc-100 hover:bg-white text-black rounded-xl font-bold transition-all shadow-xl shadow-white/5 active:scale-95"
                  >
                    <Download className="w-5 h-5" />
                    Download HD Result
                  </a>
                )}
                
                {activeVideo.error && (
                  <div className="p-4 bg-red-500/10 border border-red-500/20 rounded-xl text-red-400 text-sm">
                    <strong>Error:</strong> {activeVideo.error}
                  </div>
                )}
              </>
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
