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

    def process_batch(self, frames_bgr):
        """
        Processes a batch of frames (list of BGR images).
        Returns: list of (alpha, foreground)
        """
        if not frames_bgr:
            return []

        # Convert BGR list to a single batch tensor [B, C, H, W]
        frames_rgb = [cv2.cvtColor(f, cv2.COLOR_BGR2RGB) for f in frames_bgr]
        batch_tensor = torch.stack([
            torch.from_numpy(f).permute(2, 0, 1).float().div(255) 
            for f in frames_rgb
        ]).to(self.device)

        with torch.no_grad():
            fgr, pha, *self.rec = self.model(batch_tensor, *self.rec, downsample_ratio=0.25)
        
        # Split batch back to list
        alphas = pha.squeeze(1).cpu().numpy() # [B, H, W]
        foregrounds = fgr.cpu().permute(0, 2, 3, 1).numpy() # [B, H, W, 3]
        
        return list(zip(alphas, foregrounds))

    def reset_states(self):
        self.rec = [None] * 4

if __name__ == "__main__":
    # Test loading
    model_path = os.path.join(os.path.dirname(__file__), 'model', 'rvm_mobilenetv3.pth')
    inference = RVMInference(model_path)
    print("Model loaded successfully.")
