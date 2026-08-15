import os
import pickle
import numpy as np
from PIL import Image
import torch
import faiss
from transformers import CLIPProcessor, CLIPModel

class SareeSearchEngine:
    def __init__(self, index_path="D:/TaliorTalk/data/saree_index.pkl", 
                 clip_index_path="D:/TaliorTalk/data/clip_index.faiss",
                 color_index_path="D:/TaliorTalk/data/color_index.faiss"):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        print(f"Loading search engine indexes... Device: {self.device}")
        
        # Load metadata
        with open(index_path, 'rb') as f:
            self.data = pickle.load(f)
        self.metadata = self.data["metadata"]
        self.ntotal = len(self.metadata)
        
        # Load FAISS indexes
        self.clip_index = faiss.read_index(clip_index_path)
        self.color_index = faiss.read_index(color_index_path)
        
        # Load CLIP model (Offline-first to prevent network hangs)
        try:
            self.model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32", local_files_only=True).to(self.device)
            self.processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32", local_files_only=True)
        except Exception:
            print("Cached CLIP model not found. Fetching from Hugging Face Hub...")
            self.model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32").to(self.device)
            self.processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
        
    def get_color_layout_embedding(self, image, grid_size=(8, 8)):
        img_resized = image.resize(grid_size, Image.Resampling.LANCZOS)
        img_rgb = img_resized.convert("RGB")
        arr = np.array(img_rgb).astype(np.float32) / 255.0
        vec = arr.flatten()
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec

    def search(self, query_image=None, query_text=None, top_k=5, w_clip=0.7, w_color=0.3):
        """
        Executes a high-fidelity visual and semantic search.
        Fuses visual style (CLIP image), spatial color layout (Color grid),
        and semantic description (CLIP text) along with keyword boosting if provided.
        """
        if query_image is None and query_text is None:
            raise ValueError("Must provide either query_image or query_text")
            
        # Initialize scores arrays
        clip_img_scores = np.zeros(self.ntotal)
        clip_txt_scores = np.zeros(self.ntotal)
        color_scores = np.zeros(self.ntotal)
        keyword_boosts = np.zeros(self.ntotal)
        
        has_image = query_image is not None
        has_text = query_text is not None and len(str(query_text).strip()) > 0
        
        # 1. Process Image Query (CLIP Image + Color Grid)
        if has_image:
            if isinstance(query_image, str):
                img = Image.open(query_image)
            else:
                img = query_image
                
            # Extract Color Grid embedding
            color_vec = self.get_color_layout_embedding(img).reshape(1, -1).astype('float32')
            color_D, color_I = self.color_index.search(color_vec, self.ntotal)
            color_scores[color_I[0]] = color_D[0]
            
            # Extract CLIP image embedding
            img_rgb = img.convert("RGB")
            inputs = self.processor(images=img_rgb, return_tensors="pt").to(self.device)
            with torch.no_grad():
                image_features = self.model.get_image_features(**inputs).pooler_output
            clip_img_vec = image_features.cpu().numpy().astype('float32')
            clip_img_norm = np.linalg.norm(clip_img_vec)
            if clip_img_norm > 0:
                clip_img_vec = clip_img_vec / clip_img_norm
                
            clip_img_D, clip_img_I = self.clip_index.search(clip_img_vec, self.ntotal)
            clip_img_scores[clip_img_I[0]] = clip_img_D[0]
            
        # 2. Process Text Query (CLIP Text + Keyword Boosting)
        if has_text:
            inputs = self.processor(text=[query_text], return_tensors="pt", padding=True).to(self.device)
            with torch.no_grad():
                text_features = self.model.get_text_features(**inputs).pooler_output
            clip_txt_vec = text_features.cpu().numpy().astype('float32')
            clip_txt_norm = np.linalg.norm(clip_txt_vec)
            if clip_txt_norm > 0:
                clip_txt_vec = clip_txt_vec / clip_txt_norm
                
            clip_txt_D, clip_txt_I = self.clip_index.search(clip_txt_vec, self.ntotal)
            clip_txt_scores[clip_txt_I[0]] = clip_txt_D[0]
            
            # Keyword boosting: give priority to exact matches of materials or types
            query_words = set(str(query_text).lower().split())
            stopwords = {
                "saree", "saris", "sari", "with", "and", "in", "of", "the", "a", "for", "colour", 
                "color", "similar", "find", "show", "me", "like", "but", "this"
            }
            keywords = query_words - stopwords
            
            if keywords:
                for idx, item in enumerate(self.metadata):
                    name_lower = str(item["name"]).lower()
                    match_count = sum(1 for kw in keywords if kw in name_lower)
                    if match_count > 0:
                        # Add a small boost of +0.08 per keyword (up to +0.24 max)
                        keyword_boosts[idx] = min(match_count * 0.08, 0.24)
                        
        # 3. Fuse scores based on query type
        if has_image and has_text:
            # Fused multimodal search
            combined_clip = 0.65 * clip_img_scores + 0.35 * clip_txt_scores
            base_score = w_clip * combined_clip + w_color * color_scores
        elif has_image:
            # Pure image search
            base_score = w_clip * clip_img_scores + w_color * color_scores
        else:
            # Pure text search
            base_score = clip_txt_scores
            
        # Apply keyword boosts
        final_scores = base_score + keyword_boosts
        final_scores = np.clip(final_scores, 0.0, 1.0)
        
        # Sort results
        top_indices = np.argsort(final_scores)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            results.append({
                "filename": self.metadata[idx]["filename"],
                "relative_path": self.metadata[idx]["relative_path"],
                "name": self.metadata[idx]["name"],
                "sku": self.metadata[idx]["sku"],
                "retail_price": self.metadata[idx].get("retail_price"),
                "discounted_price": self.metadata[idx].get("discounted_price"),
                "website_link": self.metadata[idx].get("website_link"),
                "score": float(final_scores[idx]),
                "clip_score": float(clip_img_scores[idx] if has_image else clip_txt_scores[idx]),
                "color_score": float(color_scores[idx]) if has_image else 0.0
            })
            
        return results
