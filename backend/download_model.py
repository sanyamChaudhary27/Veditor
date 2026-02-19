import os
import requests
from tqdm import tqdm

def download_model(url, save_path):
    if os.path.exists(save_path):
        print(f"Model already exists at {save_path}")
        return

    print(f"Downloading model from {url}...")
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    
    with open(save_path, 'wb') as f, tqdm(
        desc=os.path.basename(save_path),
        total=total_size,
        unit='iB',
        unit_scale=True,
        unit_divisor=1024,
    ) as bar:
        for data in response.iter_content(chunk_size=1024):
            size = f.write(data)
            bar.update(size)
    print("Download complete.")

if __name__ == "__main__":
    # Robust Video Matting (RVM) models
    models = {
        "rvm_mobilenetv3.pth": "https://github.com/PeterL1n/RobustVideoMatting/releases/download/v1.0.0/rvm_mobilenetv3.pth",
        "rvm_mobilenetv3_fp32.onnx": "https://github.com/PeterL1n/RobustVideoMatting/releases/download/v1.0.0/rvm_mobilenetv3_fp32.onnx"
    }
    
    model_dir = os.path.join(os.path.dirname(__file__), "model")
    os.makedirs(model_dir, exist_ok=True)
    
    for name, url in models.items():
        save_path = os.path.join(model_dir, name)
        download_model(url, save_path)
