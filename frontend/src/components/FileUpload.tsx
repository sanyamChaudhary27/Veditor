"use client";

import { useState, useCallback } from "react";
import { useDropzone } from "react-dropzone";

interface FileUploadProps {
  onFilesSelect: (files: File[]) => void;
  accept: Record<string, string[]>;
  label: string;
}

export default function FileUpload({ onFilesSelect, accept, label }: FileUploadProps) {
  const [fileCount, setFileCount] = useState<number>(0);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      setFileCount(prev => prev + acceptedFiles.length);
      onFilesSelect(acceptedFiles);
    }
  }, [onFilesSelect]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept,
    multiple: true,
  });

  return (
    <div
      {...getRootProps()}
      className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all duration-300 ${
        isDragActive
          ? "border-blue-500 bg-blue-500/10"
          : "border-gray-700 hover:border-blue-400 hover:bg-gray-800/50"
      }`}
    >
      <input {...getInputProps()} />
      <div className="flex flex-col items-center justify-center space-y-4">
        <div className="p-4 bg-gray-800 rounded-full text-blue-400">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            className="h-8 w-8"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
            />
          </svg>
        </div>
        <div>
          <p className="text-lg font-medium text-gray-200">
            {fileCount > 0 ? `${fileCount} video(s) selected` : label}
          </p>
          <p className="text-sm text-gray-400 mt-1">
            {isDragActive ? "Drop the files here" : "Drag & drop or click to select multiple"}
          </p>
        </div>
      </div>
    </div>
  );
}
