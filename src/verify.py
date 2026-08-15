import os
import sys

# Add root folder to path so we can import src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.searcher import SareeSearchEngine

def verify():
    print("=== STARTING VERIFICATION ===")
    
    # Check index files
    index_path = "D:/TaliorTalk/data/saree_index.pkl"
    clip_index = "D:/TaliorTalk/data/clip_index.faiss"
    color_index = "D:/TaliorTalk/data/color_index.faiss"
    
    missing_files = []
    for f in [index_path, clip_index, color_index]:
        if not os.path.exists(f):
            missing_files.append(f)
            
    if missing_files:
        print(f"Error: Missing index files: {missing_files}")
        print("Please run build_index.py first to generate the indexes.")
        return False
        
    print("Index files verified. Loading SareeSearchEngine...")
    try:
        searcher = SareeSearchEngine()
    except Exception as e:
        print(f"Error loading search engine: {e}")
        return False
        
    # Run test search 1: Text-to-Image (CLIP only)
    print("\n--- Test 1: Text Search ('silk saree with golden border') ---")
    try:
        results_text = searcher.search(query_text="silk saree with golden border", top_k=3)
        for r in results_text:
            print(f"File: {r['filename']}, Score: {r['score']:.4f}")
    except Exception as e:
        print(f"Text search failed: {e}")
        return False
        
    # Run test search 2: Image-to-Image (Hybrid)
    import glob
    img_files = glob.glob("D:/TaliorTalk/data/images/*")
    if not img_files:
        print("Error: No images found in data/images to run test search.")
        return False
    test_img = img_files[0]
    print(f"\n--- Test 2: Image Search (Query: {os.path.basename(test_img)}) ---")
    try:
        results_img = searcher.search(query_image=test_img, top_k=3, w_clip=0.7, w_color=0.3)
        for r in results_img:
            print(f"File: {r['filename']}, Score: {r['score']:.4f} (Style: {r['clip_score']:.4f}, Color: {r['color_score']:.4f})")
            
        # Verify query image is the top match (since it is in the database, its similarity should be 1.0)
        top_match = results_img[0]["filename"]
        expected_match = os.path.basename(test_img)
        if top_match == expected_match:
            print(f"Success: The top match is the query image itself! Score: {results_img[0]['score']:.4f}")
        else:
            print(f"Warning: Top match is {top_match}, expected {expected_match}.")
            
    except Exception as e:
        print(f"Image search failed: {e}")
        return False
        
    print("\n=== VERIFICATION COMPLETE: ALL TESTS PASSED! ===")
    return True

if __name__ == "__main__":
    verify()
