import requests
import os

def test_download():
    # Try to find the latest output file
    output_dir = "outputs"
    files = [f for f in os.listdir(output_dir) if f.startswith("out_")]
    if not files:
        print("No output files found.")
        return

    latest_file = files[0] # Just take the first one for testing
    url = f"http://localhost:8000/download/{latest_file}"
    
    print(f"Testing download from {url}...")
    try:
        response = requests.get(url)
        if response.status_code == 200:
            print(f"Download successful! File size: {len(response.content)} bytes")
        else:
            print(f"Download failed with status {response.status_code}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    test_download()
