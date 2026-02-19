import cv2
import numpy as np
import requests
import os

def create_test_video(path, duration=2, fps=30):
    width, height = 640, 480
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(path, fourcc, fps, (width, height))

    for i in range(duration * fps):
        # Create a frame with a white background
        frame = np.full((height, width, 3), 255, dtype=np.uint8)
        
        # Draw a moving "subject" (a blue circle)
        center = (int(width/2 + 50 * np.sin(i/10)), int(height/2 + 50 * np.cos(i/10)))
        cv2.circle(frame, center, 50, (255, 0, 0), -1)
        
        out.write(frame)
    
    out.release()
    print(f"Test video created at {path}")

def test_endpoint():
    video_path = "test_input.mp4"
    if not os.path.exists(video_path):
        create_test_video(video_path)

    url = "http://localhost:8000/remove-background"
    files = {'video': open(video_path, 'rb')}
    data = {
        'color_r': 0, 
        'color_g': 0, 
        'color_b': 0, 
        'blur_radius': 50, 
        'lighting_strength': 0.8
    } # Black background with blur and lighting match

    print(f"Sending request to {url}...")
    try:
        response = requests.post(url, files=files, data=data)
        if response.status_code == 200:
            print("Request successful!")
            print("Response:", response.json())
        else:
            print(f"Request failed with status {response.status_code}")
            print("Error:", response.text)
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    test_endpoint()
