import os
import requests
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
from PIL import Image
from io import BytesIO

CSV_PATH = "D:/TaliorTalk/saree_dataset.csv"
IMAGE_DIR = "D:/TaliorTalk/data/images"

def download_image(row):
    sku = str(row['SKU']).strip()
    url = str(row['image_url']).strip()
    if not url or not url.startswith('http'):
        return sku, "Invalid URL"
        
    ext = "webp"
    if ".png" in url.lower():
        ext = "png"
    elif ".jpg" in url.lower() or ".jpeg" in url.lower():
        ext = "jpg"
        
    out_path = os.path.join(IMAGE_DIR, f"{sku}.{ext}")
    if os.path.exists(out_path):
        return sku, "Already exists"
        
    try:
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            # Verify image is valid and not corrupted
            img = Image.open(BytesIO(response.content))
            img.verify()
            
            with open(out_path, 'wb') as f:
                f.write(response.content)
            return sku, "Success"
        else:
            return sku, f"Status code {response.status_code}"
    except Exception as e:
        return sku, f"Error: {e}"

def main():
    os.makedirs(IMAGE_DIR, exist_ok=True)
    df = pd.read_csv(CSV_PATH)
    print(f"Loaded CSV with {len(df)} rows. Starting download...")
    
    # Drop rows without SKU or image_url
    df = df.dropna(subset=['SKU', 'image_url'])
    rows = df.to_dict('records')
    
    success_count = 0
    fail_count = 0
    exists_count = 0
    
    with ThreadPoolExecutor(max_workers=24) as executor:
        futures = {executor.submit(download_image, row): row for row in rows}
        for i, future in enumerate(as_completed(futures)):
            sku, status = future.result()
            if status == "Success":
                success_count += 1
            elif status == "Already exists":
                exists_count += 1
            else:
                fail_count += 1
                
            if (i + 1) % 100 == 0 or (i + 1) == len(rows):
                print(f"Progress: {i+1}/{len(rows)} processed. (New: {success_count}, Existing: {exists_count}, Failed: {fail_count})")
                
    print(f"Finished downloading. Success: {success_count}, Existing: {exists_count}, Failed: {fail_count}")

if __name__ == "__main__":
    main()
