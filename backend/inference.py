import torch
import sys
import os
import cv2
import numpy as np
from PIL import Image
from torchvision.transforms import ToTensor

# Add rvm_repo to path to import model
sys.path.append(os.path.join(os.path.dirname(__file__), 'rvm_repo'))
from model import MattingNetwork

class RVMInference:
    def __init__(self, model_path, device=None):
        if device is None:
            self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        else:
            self.device = torch.device(device)
            
        print(f"Using device: {self.device}")
        
        self.model = MattingNetwork('mobilenetv3').to(self.device).eval()
        self.model.load_state_dict(torch.load(model_path, map_location=self.device))
        self.rec = [None] * 4 # Recurrent states

    def process_frame(self, frame_bgr):
        """
        Processes a single frame (BGR from OpenCV).
        Returns: alpha, foreground
        """
        # Convert BGR to RGB and normalize to [0, 1]
        frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        
        # Direct conversion to tensor is faster than PIL
        frame_tensor = torch.from_numpy(frame_rgb).permute(2, 0, 1).float().div(255).unsqueeze(0).to(self.device)

        with torch.no_grad():
            fgr, pha, *self.rec = self.model(frame_tensor, *self.rec, downsample_ratio=0.25)
        
        # Efficiently move back to numpy for compositing if not using GPU for compositing
        alpha = pha.squeeze().cpu().numpy()
        foreground = fgr.squeeze().permute(1, 2, 0).cpu().numpy()
        
        return alpha, foreground

    def reset_states(self):
        self.rec = [None] * 4

if __name__ == "__main__":
    # Test loading
    model_path = os.path.join(os.path.dirname(__file__), 'model', 'rvm_mobilenetv3.pth')
    inference = RVMInference(model_path)
    print("Model loaded successfully.")
