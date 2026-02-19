"use client";

import { useState } from "react";
import FileUpload from "./FileUpload";

interface BackgroundPickerProps {
  onBackgroundSelect: (file: File | null) => void;
  onColorSelect: (color: { r: number; g: number; b: number }) => void;
}

const PRESET_COLORS = [
  { name: "Green", r: 0, g: 255, b: 0, hex: "#00FF00" },
  { name: "Blue", r: 0, g: 0, b: 255, hex: "#0000FF" },
  { name: "White", r: 255, g: 255, b: 255, hex: "#FFFFFF" },
  { name: "Black", r: 0, g: 0, b: 0, hex: "#000000" },
];

export default function BackgroundPicker({ onBackgroundSelect, onColorSelect }: BackgroundPickerProps) {
  const [mode, setMode] = useState<"image" | "color">("color");
  const [selectedColor, setSelectedColor] = useState(PRESET_COLORS[0]);

  return (
    <div className="bg-gray-800/50 rounded-2xl p-6 border border-gray-700/50 backdrop-blur-sm">
      <div className="flex items-center space-x-4 mb-6">
        <button
          onClick={() => setMode("color")}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
            mode === "color"
              ? "bg-blue-600 text-white shadow-lg shadow-blue-900/20"
              : "text-gray-400 hover:text-gray-200 hover:bg-gray-700"
          }`}
        >
          Solid Color
        </button>
        <button
          onClick={() => setMode("image")}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
            mode === "image"
              ? "bg-blue-600 text-white shadow-lg shadow-blue-900/20"
              : "text-gray-400 hover:text-gray-200 hover:bg-gray-700"
          }`}
        >
          Custom Image
        </button>
      </div>

      {mode === "color" ? (
        <div className="grid grid-cols-4 gap-4">
          {PRESET_COLORS.map((color) => (
            <button
              key={color.name}
              onClick={() => {
                setSelectedColor(color);
                onColorSelect({ r: color.r, g: color.g, b: color.b });
                onBackgroundSelect(null);
              }}
              className={`group flex flex-col items-center space-y-2 transition-all ${
                selectedColor.name === color.name ? "scale-105" : "opacity-60 hover:opacity-100"
              }`}
            >
              <div
                className="w-12 h-12 rounded-full border-2 border-gray-600 shadow-inner group-hover:shadow-lg transition-all"
                style={{ backgroundColor: color.hex }}
              />
              <span className="text-xs text-gray-400 font-medium">{color.name}</span>
            </button>
          ))}
        </div>
      ) : (
        <FileUpload
          label="Select background image"
          accept={{ "image/*": [".jpg", ".jpeg", ".png"] }}
          onFilesSelect={(files) => onBackgroundSelect(files[0])}
        />
      )}
    </div>
  );
}
