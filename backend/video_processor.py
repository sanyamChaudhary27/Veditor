import cv2
import os
import numpy as np
from tqdm import tqdm
from inference import RVMInference

class VideoProcessor:
    def __init__(self, model_path, device=None):
        self.inference = RVMInference(model_path, device)

    def _get_lab_stats(self, img_lab):
        """Compute mean and std for each channel in Lab color space."""
        l, a, b = cv2.split(img_lab)
        return (l.mean(), l.std()), (a.mean(), a.std()), (b.mean(), b.std())

    def apply_smart_lighting(self, foreground_bgr, background_bgr, strength=0.5):
        """
        Matches foreground lighting to background using Lab color space stats.
        strength: 0.0 (no change) to 1.0 (full match)
        """
        if strength <= 0:
            return foreground_bgr

        # Convert to Lab
        fg_lab = cv2.cvtColor(foreground_bgr.astype(np.uint8), cv2.COLOR_BGR2LAB).astype(np.float32)
        bg_lab = cv2.cvtColor(background_bgr.astype(np.uint8), cv2.COLOR_BGR2LAB).astype(np.float32)

        fg_stats = self._get_lab_stats(fg_lab)
        bg_stats = self._get_lab_stats(bg_lab)

        res_lab_list = list(cv2.split(fg_lab))
        for i in range(3):
            # Normalization and scaling
            mu_f, sigma_f = fg_stats[i]
            mu_b, sigma_b = bg_stats[i]
            
            # Avoid division by zero
            if sigma_f < 1e-4: sigma_f = 1e-4
            
            # Transfer: (x - mu_f) * (sigma_b / sigma_f) + mu_b
            matched_channel = (res_lab_list[i] - mu_f) * (sigma_b / sigma_f) + mu_b
            
            # Blend based on strength
            res_lab_list[i] = matched_channel * strength + res_lab_list[i] * (1 - strength)

        res_lab = cv2.merge(res_lab_list)
        res_lab = np.clip(res_lab, 0, 255).astype(np.uint8)
        return cv2.cvtColor(res_lab, cv2.COLOR_LAB2BGR)

    def process_single_frame(self, frame_bgr, background_path=None, 
                             background_color=(0, 255, 0), blur_radius=0, lighting_strength=0.0):
        """Processes a single frame for preview purposes."""
        height, width = frame_bgr.shape[:2]
        
        # Setup background
        if background_path and os.path.exists(background_path):
            bg_img = cv2.imread(background_path)
            bg_img = cv2.resize(bg_img, (width, height))
        else:
            bg_img = np.full((height, width, 3), background_color, dtype=np.uint8)

        if blur_radius > 0:
            ksize = int(blur_radius * 2 + 1)
            bg_img = cv2.GaussianBlur(bg_img, (ksize, ksize), 0)

        bg_img_f = bg_img.astype(np.float32) / 255.0
        
        # Inference
        self.inference.reset_states()
        alphas, foregrounds = self.inference.process_batch([frame_bgr])[0]
        
        # Composite
        foreground_bgr_f = foregrounds[:, :, ::-1]
        
        if lighting_strength > 0:
            fg_u8 = (foreground_bgr_f * 255).astype(np.uint8)
            fg_matched = self.apply_smart_lighting(fg_u8, bg_img, strength=lighting_strength)
            foreground_bgr_f = fg_matched.astype(np.float32) / 255.0

        alpha = alphas[:, :, np.newaxis]
        composite = (foreground_bgr_f * alpha + bg_img_f * (1 - alpha))
        return (composite * 255).astype(np.uint8)

    def process_video(self, input_path, output_path, background_path=None, 
                      background_color=(0, 255, 0), blur_radius=0, lighting_strength=0.0,
                      progress_callback=None):
        
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
            bg_img = np.full((height, width, 3), background_color, dtype=np.uint8)

        # Apply Blur if needed
        if blur_radius > 0:
            # Ensure blur radius is odd
            ksize = int(blur_radius * 2 + 1)
            bg_img = cv2.GaussianBlur(bg_img, (ksize, ksize), 0)

        bg_img_f = bg_img.astype(np.float32) / 255.0

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

        self.inference.reset_states()
        
        batch_size = 4
        frames_batch = []
        processed_count = 0
        
        pbar = tqdm(total=total_frames, desc="Processing Video (Batched)")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                # Process remaining frames in batch
                if frames_batch:
                    results = self.inference.process_batch(frames_batch)
                    for i, (alpha, foreground) in enumerate(results):
                        self._write_frame(out, foreground, alpha, bg_img_f, bg_img, lighting_strength)
                        processed_count += 1
                        pbar.update(1)
                        if progress_callback:
                            progress_callback(processed_count, total_frames)
                break

            frames_batch.append(frame)
            
            if len(frames_batch) == batch_size:
                results = self.inference.process_batch(frames_batch)
                for i, (alpha, foreground) in enumerate(results):
                    self._write_frame(out, foreground, alpha, bg_img_f, bg_img, lighting_strength)
                    processed_count += 1
                    pbar.update(1)
                    if progress_callback:
                        progress_callback(processed_count, total_frames)
                frames_batch = []

        cap.release()
        out.release()
        pbar.close()

    def _write_frame(self, out, foreground, alpha, bg_img_f, bg_img_orig, lighting_strength):
        # Convert foreground to BGR
        foreground_bgr_f = foreground[:, :, ::-1] # RGB to BGR

        # Apply Lighting Match
        if lighting_strength > 0:
            # Convert [0, 1] float back to [0, 255] uint8 for color transfer
            fg_u8 = (foreground_bgr_f * 255).astype(np.uint8)
            fg_matched = self.apply_smart_lighting(fg_u8, bg_img_orig, strength=lighting_strength)
            foreground_bgr_f = fg_matched.astype(np.float32) / 255.0

        # Composite
        alpha = alpha[:, :, np.newaxis]
        composite = (foreground_bgr_f * alpha + bg_img_f * (1 - alpha))
        out.write((composite * 255).astype(np.uint8))
