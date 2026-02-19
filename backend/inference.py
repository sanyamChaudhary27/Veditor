import os
import cv2
import numpy as np
import onnxruntime as ort

class RVMInference:
    def __init__(self, model_path_pth, device='cpu'):
        # Prefer ONNX if available for speed
        model_dir = os.path.dirname(model_path_pth)
        onnx_path = os.path.join(model_dir, "rvm_mobilenetv3_fp32.onnx")
        
        self.use_onnx = os.path.exists(onnx_path)
        if self.use_onnx:
            print(f"Using ONNX Runtime for inference: {onnx_path}")
            self.sess = ort.InferenceSession(onnx_path, providers=['CPUExecutionProvider'])
            self.rec = {
                'r1i': np.zeros([1, 16, 1, 1], dtype=np.float32),
                'r2i': np.zeros([1, 20, 1, 1], dtype=np.float32),
                'r3i': np.zeros([1, 40, 1, 1], dtype=np.float32),
                'r4i': np.zeros([1, 64, 1, 1], dtype=np.float32)
            }
        else:
            print("ONNX model not found, falling back to PyTorch (Slower)")
            import torch
            import sys
            sys.path.append(os.path.join(os.path.dirname(__file__), 'rvm_repo'))
            from model import MattingNetwork
            self.device = torch.device('cuda' if torch.cuda.is_available() and device == 'cuda' else 'cpu')
            self.model = MattingNetwork('mobilenetv3').to(self.device).eval()
            self.model.load_state_dict(torch.load(model_path_pth, map_location=self.device))
            self.rec = [None] * 4

    def reset_states(self):
        if self.use_onnx:
            self.rec = {
                'r1i': np.zeros([1, 16, 1, 1], dtype=np.float32),
                'r2i': np.zeros([1, 20, 1, 1], dtype=np.float32),
                'r3i': np.zeros([1, 40, 1, 1], dtype=np.float32),
                'r4i': np.zeros([1, 64, 1, 1], dtype=np.float32)
            }
        else:
            self.rec = [None] * 4

    def process_batch(self, frames_bgr):
        if not frames_bgr:
            return []

        # Enforce 3 channels and convert to RGB
        frames_rgb = []
        for f in frames_bgr:
            if f.shape[2] == 4:
                f = cv2.cvtColor(f, cv2.COLOR_BGRA2BGR)
            frames_rgb.append(cv2.cvtColor(f, cv2.COLOR_BGR2RGB))

        if self.use_onnx:
            return self._process_onnx(frames_rgb)
        else:
            return self._process_torch(frames_rgb)

    def _process_onnx(self, frames_rgb):
        results = []
        downsample_ratio = np.array([0.25], dtype=np.float32)
        
        for frame in frames_rgb:
            # ONNX expects [1, C, H, W]
            src = np.expand_dims(frame.transpose(2, 0, 1), 0).astype(np.float32) / 255.0
            
            inputs = {
                'src': src,
                'r1i': self.rec['r1i'],
                'r2i': self.rec['r2i'],
                'r3i': self.rec['r3i'],
                'r4i': self.rec['r4i'],
                'downsample_ratio': downsample_ratio
            }
            
            fgr, pha, r1o, r2o, r3o, r4o = self.sess.run(None, inputs)
            
            self.rec = {'r1i': r1o, 'r2i': r2o, 'r3i': r3o, 'r4i': r4o}
            
            # Convert back: pha [1, 1, H, W] -> [H, W], fgr [1, 3, H, W] -> [H, W, 3]
            alpha = pha[0, 0]
            foreground = fgr[0].transpose(1, 2, 0)
            results.append((alpha, foreground))
            
        return results

    def _process_torch(self, frames_rgb):
        import torch
        batch_tensor = torch.stack([
            torch.from_numpy(f).permute(2, 0, 1).float().div(255) 
            for f in frames_rgb
        ]).to(self.device)

        with torch.no_grad():
            fgr, pha, *self.rec = self.model(batch_tensor, *self.rec, downsample_ratio=0.25)
        
        alphas = pha.squeeze(1).cpu().numpy()
        foregrounds = fgr.cpu().permute(0, 2, 3, 1).numpy()
        
        return list(zip(alphas, foregrounds))
