import cv2
import os
import numpy as np
from tqdm import tqdm
from inference import RVMInference
import subprocess
import tempfile

class VideoProcessor:
    def __init__(self, model_path, device=None):
        self.inference = RVMInference(model_path, device)

    def _get_lab_stats(self, img_lab):
        """Compute mean and std for each channel in Lab color space."""
        l, a, b = cv2.split(img_lab)
        return (l.mean(), l.std()), (a.mean(), a.std()), (b.mean(), b.std())

    def apply_smart_lighting(self, foreground_bgr, bg_stats, strength=0.5):
        """
        Matches foreground lighting to background using pre-computed Lab stats.
        """
        if strength <= 0:
            return foreground_bgr

        # Convert to Lab
        fg_lab = cv2.cvtColor(foreground_bgr.astype(np.uint8), cv2.COLOR_BGR2LAB).astype(np.float32)
        fg_stats = self._get_lab_stats(fg_lab)

        res_lab_list = list(cv2.split(fg_lab))
        for i in range(3):
            mu_f, sigma_f = fg_stats[i]
            mu_b, sigma_b = bg_stats[i]
            
            if sigma_f < 1e-4: sigma_f = 1e-4
            
            matched_channel = (res_lab_list[i] - mu_f) * (sigma_b / sigma_f) + mu_b
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
        
        # Precompute BG stats for lighting match
        bg_stats = None
        if lighting_strength > 0:
            bg_lab = cv2.cvtColor(bg_img.astype(np.uint8), cv2.COLOR_BGR2LAB).astype(np.float32)
            bg_stats = self._get_lab_stats(bg_lab)

        # Inference
        self.inference.reset_states()
        alphas, foregrounds = self.inference.process_batch([frame_bgr])[0]
        
        # Composite
        foreground_bgr_f = foregrounds[:, :, ::-1]
        
        if lighting_strength > 0:
            fg_u8 = (foreground_bgr_f * 255).astype(np.uint8)
            fg_matched = self.apply_smart_lighting(fg_u8, bg_stats, strength=lighting_strength)
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
        
        # Validate video properties
        if fps <= 0:
            fps = 30  # Default fallback
        if total_frames <= 0:
            raise Exception(f"Invalid video: 0 frames detected")
        if width <= 0 or height <= 0:
            raise Exception(f"Invalid video dimensions: {width}x{height}")

        # Extract audio from input video
        audio_path = None
        temp_dir = tempfile.gettempdir()
        audio_path = os.path.join(temp_dir, f"audio_{os.path.basename(input_path)}.aac")
        
        # Try to find ffmpeg
        ffmpeg_path = None
        for path in ['ffmpeg', 'C:\\ffmpeg\\ffmpeg.exe', '/usr/bin/ffmpeg', '/usr/local/bin/ffmpeg']:
            try:
                result = subprocess.run([path, '-version'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=5)
                if result.returncode == 0:
                    ffmpeg_path = path
                    break
            except:
                continue
        
        try:
            if ffmpeg_path:
                # Try to extract audio using ffmpeg
                subprocess.run(
                    [ffmpeg_path, '-i', input_path, '-q:a', '9', '-n', audio_path],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    timeout=30
                )
            if not os.path.exists(audio_path) or os.path.getsize(audio_path) == 0:
                audio_path = None
                print("No audio track found in input video")
        except Exception as e:
            print(f"Could not extract audio: {e}")
            audio_path = None

        # Setup background
        if background_path and os.path.exists(background_path):
            bg_img = cv2.imread(background_path)
            bg_img = cv2.resize(bg_img, (width, height))
        else:
            bg_img = np.full((height, width, 3), background_color, dtype=np.uint8)

        # Apply Blur if needed
        if blur_radius > 0:
            ksize = int(blur_radius * 2 + 1)
            bg_img = cv2.GaussianBlur(bg_img, (ksize, ksize), 0)

        bg_img_f = bg_img.astype(np.float32) / 255.0
        
        # Precompute BG stats for lighting match
        bg_stats = None
        if lighting_strength > 0:
            bg_lab = cv2.cvtColor(bg_img.astype(np.uint8), cv2.COLOR_BGR2LAB).astype(np.float32)
            bg_stats = self._get_lab_stats(bg_lab)

        # Create temporary video file without audio
        temp_video_path = os.path.join(temp_dir, f"temp_video_{os.path.basename(output_path)}")
        
        # Try multiple codecs for better compatibility
        # MJPEG is most reliable but larger file size
        # mp4v is best for MP4 but requires proper frame format
        codecs = ['MJPG', 'mp4v', 'H264', 'DIVX']
        out = None
        
        for codec in codecs:
            try:
                fourcc = cv2.VideoWriter_fourcc(*codec)
                out = cv2.VideoWriter(temp_video_path, fourcc, fps, (width, height))
                if out.isOpened():
                    print(f"Using codec: {codec}")
                    break
                else:
                    out = None
            except Exception as e:
                print(f"Codec {codec} failed: {e}")
                continue
        
        if out is None or not out.isOpened():
            cap.release()
            raise Exception(f"Failed to initialize video writer. No compatible codec found.")

        self.inference.reset_states()
        
        batch_size = 4
        frames_batch = []
        processed_count = 0
        frames_written = 0
        
        pbar = tqdm(total=total_frames, desc="Processing Video (Batched)")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                if frames_batch:
                    results = self.inference.process_batch(frames_batch)
                    for i, (alpha, foreground) in enumerate(results):
                        try:
                            self._write_frame(out, foreground, alpha, bg_img_f, bg_stats, lighting_strength)
                            frames_written += 1
                        except Exception as e:
                            print(f"Error writing frame: {e}")
                        processed_count += 1
                        pbar.update(1)
                        if progress_callback:
                            progress_callback(processed_count, total_frames)
                break

            frames_batch.append(frame)
            
            if len(frames_batch) == batch_size:
                results = self.inference.process_batch(frames_batch)
                for i, (alpha, foreground) in enumerate(results):
                    try:
                        self._write_frame(out, foreground, alpha, bg_img_f, bg_stats, lighting_strength)
                        frames_written += 1
                    except Exception as e:
                        print(f"Error writing frame: {e}")
                    processed_count += 1
                    pbar.update(1)
                    if progress_callback:
                        progress_callback(processed_count, total_frames)
                frames_batch = []

        cap.release()
        out.release()
        pbar.close()
        
        if frames_written == 0:
            raise Exception("No frames were written to output video. Check model inference output.")
        
        print(f"Video processing complete. {frames_written} frames written.")
        
        # Verify temp video has content
        if os.path.exists(temp_video_path):
            temp_size = os.path.getsize(temp_video_path)
            print(f"Temp video file size: {temp_size} bytes")
            if temp_size < 1000:
                raise Exception(f"Temp video file is too small ({temp_size} bytes). Video encoding may have failed.")
        else:
            raise Exception("Temp video file was not created")
        
        # Combine video with audio if audio was extracted
        if audio_path and os.path.exists(audio_path):
            print("Reattaching audio to video...")
            print(f"Video file: {temp_video_path}")
            print(f"Audio file: {audio_path}")
            try:
                if ffmpeg_path:
                    # Re-encode video to ensure compatibility, then add audio
                    result = subprocess.run(
                        [ffmpeg_path, '-i', temp_video_path, '-i', audio_path, '-c:v', 'libx264', '-preset', 'fast', '-c:a', 'aac', '-map', '0:v:0', '-map', '1:a:0', '-y', output_path],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        timeout=120
                    )
                    if result.returncode != 0:
                        print(f"FFmpeg error: {result.stderr.decode()}")
                        # Fallback: just use the temp video without audio
                        if os.path.exists(temp_video_path):
                            os.rename(temp_video_path, output_path)
                    else:
                        print("FFmpeg completed successfully")
                # Clean up temp files
                if os.path.exists(temp_video_path):
                    try:
                        os.remove(temp_video_path)
                    except:
                        pass
                if os.path.exists(audio_path):
                    try:
                        os.remove(audio_path)
                    except:
                        pass
                print("Audio reattached successfully!")
            except Exception as e:
                print(f"Could not reattach audio: {e}. Using video without audio.")
                # Fallback: just use the temp video
                if os.path.exists(temp_video_path):
                    os.rename(temp_video_path, output_path)
        else:
            # No audio, just move temp video to output
            if os.path.exists(temp_video_path):
                os.rename(temp_video_path, output_path)

    def _write_frame(self, out, foreground, alpha, bg_img_f, bg_stats, lighting_strength):
        # Ensure correct range [0, 1] and shape
        alpha = np.clip(alpha, 0, 1)
        foreground = np.clip(foreground, 0, 1)
        
        target_h, target_w = bg_img_f.shape[:2]
        
        # Resize if model output doesn't match input exactly (unlikely but safe)
        if alpha.shape[:2] != (target_h, target_w):
            alpha = cv2.resize(alpha, (target_w, target_h))
        if foreground.shape[:2] != (target_h, target_w):
            foreground = cv2.resize(foreground, (target_w, target_h))

        foreground_bgr_f = foreground[:, :, ::-1] # RGB to BGR

        if lighting_strength > 0 and bg_stats is not None:
            fg_u8 = (foreground_bgr_f * 255).astype(np.uint8)
            fg_matched = self.apply_smart_lighting(fg_u8, bg_stats, strength=lighting_strength)
            foreground_bgr_f = fg_matched.astype(np.float32) / 255.0

        alpha = alpha[:, :, np.newaxis]
        composite = (foreground_bgr_f * alpha + bg_img_f * (1 - alpha))
        
        final_frame = (np.clip(composite, 0, 1) * 255).astype(np.uint8)
        
        # Verify frame is valid before writing
        if final_frame.shape != (target_h, target_w, 3):
            raise ValueError(f"Invalid frame shape: {final_frame.shape}, expected ({target_h}, {target_w}, 3)")
        
        # Ensure frame is contiguous in memory (required by some codecs)
        final_frame = np.ascontiguousarray(final_frame)
        
        out.write(final_frame)
