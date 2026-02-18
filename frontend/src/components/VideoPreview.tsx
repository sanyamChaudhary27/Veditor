"use client";

import { useEffect, useRef } from "react";

interface VideoPreviewProps {
  videoFile?: File | null;
  processedVideoUrl?: string | null;
  title: string;
}

export default function VideoPreview({ videoFile, processedVideoUrl, title }: VideoPreviewProps) {
  const videoRef = useRef<HTMLVideoElement>(null);

  useEffect(() => {
    if (videoFile && videoRef.current) {
      const url = URL.createObjectURL(videoFile);
      videoRef.current.src = url;
      return () => URL.revokeObjectURL(url);
    }
  }, [videoFile]);

  return (
    <div className="flex flex-col space-y-2">
      <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider">
        {title}
      </h3>
      <div className="relative aspect-video bg-gray-900 rounded-xl overflow-hidden border border-gray-800 shadow-2xl">
        {videoFile || processedVideoUrl ? (
          <video
            ref={videoRef}
            src={processedVideoUrl || undefined}
            controls
            className="w-full h-full object-contain"
          />
        ) : (
          <div className="absolute inset-0 flex items-center justify-center">
            <p className="text-gray-600 italic">No video selected</p>
          </div>
        )}
      </div>
    </div>
  );
}
