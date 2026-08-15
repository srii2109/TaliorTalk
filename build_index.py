import os
import pickle
import pandas as pd
import numpy as np
from PIL import Image
import torch
import faiss
from transformers import CLIPProcessor, CLIPModel

# Set paths
IMAGE_DIR = "D:/TaliorTalk/data/images"
INDEX_PATH = "D:/TaliorTalk/data/saree_index.pkl"
CSV_PATH = "D:/TaliorTalk/saree_dataset.csv"

def get_color_layout_embedding(image, grid_size=(8, 8)):
    img_resized = image.resize(grid_size, Image.Resampling.LANCZOS)
    img_rgb = img_resized.convert("RGB")
    arr = np.array(img_rgb).astype(np.float32) / 255.0
    vec = arr.flatten()
    norm = np.linalg.norm(vec)
    if norm > 0:
        vec = vec / norm
    return vec

def find_image_for_sku(sku):
    for ext in ['webp', 'jpg', 'png', 'jpeg']:
        p = os.path.join(IMAGE_DIR, f"{sku}.{ext}")
        if os.path.exists(p):
            return p, f"{sku}.{ext}"
    return None, None

def build_index():
    print("Loading CLIP model and processor...")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {device}")
    
    model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32").to(device)
    processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
    
    # Read CSV
    df = pd.read_csv(CSV_PATH).dropna(subset=['SKU', 'image_url']).drop_duplicates(subset=['SKU'])
    print(f"Loaded CSV with {len(df)} rows. Mapping to local images...")
    
    clip_embeddings = []
    color_embeddings = []
    metadata = []
    
    rows = df.to_dict('records')
    
    for i, row in enumerate(rows):
        sku = str(row['SKU']).strip()
        img_path, filename = find_image_for_sku(sku)
        
        if not img_path:
            # Image failed to download or was skipped
            continue
            
        try:
            img = Image.open(img_path)
            
            # 1. Extract Color Layout Embedding
            color_vec = get_color_layout_embedding(img)
            
            # 2. Extract CLIP Image Embedding
            img_rgb = img.convert("RGB")
            inputs = processor(images=img_rgb, return_tensors="pt").to(device)
            with torch.no_grad():
                image_features = model.get_image_features(**inputs).pooler_output
            
            clip_vec = image_features.cpu().numpy()[0]
            clip_norm = np.linalg.norm(clip_vec)
            if clip_norm > 0:
                clip_vec = clip_vec / clip_norm
                
            clip_embeddings.append(clip_vec)
            color_embeddings.append(color_vec)
            
            metadata.append({
                "name": row.get('Name', ''),
                "sku": sku,
                "retail_price": row.get('Retail Price', ''),
                "discounted_price": row.get('Discounted Price', ''),
                "image_url": row.get('image_url', ''),
                "website_link": row.get('Website Link', ''),
                "filename": filename,
                "relative_path": f"data/images/{filename}"
            })
            
            if (len(metadata)) % 100 == 0 or (i + 1) == len(rows):
                print(f"Indexed {len(metadata)} images...")
                
        except Exception as e:
            print(f"Error processing image for SKU {sku}: {e}")
            
    if not clip_embeddings:
        print("Error: No images were successfully processed and indexed!")
        return
        
    # Convert lists to numpy arrays
    clip_embeddings = np.array(clip_embeddings).astype('float32')
    color_embeddings = np.array(color_embeddings).astype('float32')
    
    print(f"Building FAISS indexes for {len(metadata)} items...")
    clip_index = faiss.IndexFlatIP(512)
    clip_index.add(clip_embeddings)
    
    color_index = faiss.IndexFlatIP(192)
    color_index.add(color_embeddings)
    
    # Save indexes and metadata to pickle
    index_data = {
        "clip_embeddings": clip_embeddings,
        "color_embeddings": color_embeddings,
        "metadata": metadata
    }
    
    os.makedirs(os.path.dirname(INDEX_PATH), exist_ok=True)
    with open(INDEX_PATH, 'wb') as f:
        pickle.dump(index_data, f)
        
    faiss.write_index(clip_index, "D:/TaliorTalk/data/clip_index.faiss")
    faiss.write_index(color_index, "D:/TaliorTalk/data/color_index.faiss")
    
    print("Indexing complete! Saved FAISS indexes and metadata.")

if __name__ == "__main__":
    build_index()
