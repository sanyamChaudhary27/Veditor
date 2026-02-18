import cv2
import os
import numpy as np
from tqdm import tqdm
from inference import RVMInference

class VideoProcessor:
    def __init__(self, model_path, device='cpu'):
        self.inference = RVMInference(model_path, device)

    def process_video(self, input_path, output_path, background_path=None, background_color=(0, 255, 0)):
        """
        Processes video to remove background and replace it with an image or color.
        """
        cap = cv2.VideoCapture(input_path)
        if not cap.isOpened():
            raise Exception(f"Could not open video {input_path}")

        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        # Setup background
        if background_path and os.path.exists(background_path):
            bg_img = cv2.imread(background_path)
            bg_img = cv2.resize(bg_img, (width, height))
        else:
            # Create solid color background
            bg_img = np.full((height, width, 3), background_color, dtype=np.uint8)

        # Pre-convert background to float32 [0, 1] for faster compositing
        bg_img_f = bg_img.astype(np.float32) / 255.0

        # Video Writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

        self.inference.reset_states()

        for _ in tqdm(range(total_frames), desc="Processing Video"):
            ret, frame = cap.read()
            if not ret:
                break

            # Inference
            alpha, foreground = self.inference.process_frame(frame)
            
            # alpha is (H, W), foreground is (H, W, 3) in range [0, 1] RGB
            # Convert foreground to BGR
            foreground_bgr = foreground[:, :, ::-1] # Swaps RGB to BGR efficiently

            # Efficient Compositing
            alpha = alpha[:, :, np.newaxis]
            composite = (foreground_bgr * alpha + bg_img_f * (1 - alpha))
            
            # Convert back to uint8 [0, 255]
            composite = (composite * 255).astype(np.uint8)

            out.write(composite)

        cap.release()
        out.release()
        print(f"Video saved to {output_path}")

if __name__ == "__main__":
    # Test stub
    # processor = VideoProcessor('backend/model/rvm_mobilenetv3.pth')
    # processor.process_video('input.mp4', 'output.mp4')
    pass
