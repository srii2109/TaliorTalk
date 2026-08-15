# TailorTalk: Luxury Saree Search Agent

TailorTalk is an AI-powered conversational search assistant designed to browse a catalog of **1,024 high-resolution saree images (649 unique product listings)**. It naturally engages with users, understands conversational fashion queries, processes uploaded images or links, and finds the closest matching sarees using a **state-of-the-art Unified Multimodal Hybrid Search Engine**.

---

## 🚀 Key Features

1. **Multimodal Conversation:** Naturally converse with the agent. The agent understands context and triggers visual search based on image uploads, links, or text descriptions.
2. **Unified Multimodal Search Fusion:** Combines deep semantic visual features (CLIP Image), semantic text queries (CLIP Text), and localized spatial color distributions (Color Grid) into a unified similarity score.
3. **Exact Keyword Boosting:** Extracts key fashion attributes (such as fabric types like *Silk*, *Organza*, *Crepe*, *Tissue*, *Pashmina*, and weaves like *Banarasi*, *Munga*, *Floral*) and applies a boost to matches that contain these keywords in their metadata.
4. **Real-time Weight Sliders:** Adjust similarity weights dynamically in the Streamlit UI to balance overall style match vs. precise color matching.
5. **FAISS Local Indexing:** Fast, self-contained vector database search with zero cloud dependencies or latency overhead.
6. **Clean Two-Column Dashboard:** Elegant glassmorphic layout: custom HTML chat bubbles on the left, visual search gallery results with dynamic fashion badges and original/discounted price cards on the right.

---

## 🛠️ Architecture & Tech Stack

- **Frontend:** Streamlit with custom glassmorphism HTML/CSS styling.
- **Conversational Agent:** Gemini (`gemini-2.5-flash`) utilizing native Function Calling (Tools).
- **Vision Embedding Model:** CLIP (`openai/clip-vit-base-patch32`) from Hugging Face Transformers.
- **Color Layout Descriptor:** 8x8 Spatial Color Grid representation.
- **Vector Database:** FAISS (`faiss-cpu`) with Inner Product (IP) index for cosine similarity matching.

---

## 💡 Search Quality Improvements

A standard visual embedding search (e.g. using a global CNN or standard CLIP) often fails to capture the nuances of sarees, because all sarees share a similar silhouette and shape. To achieve premium matching quality, we implemented a **Unified Scoring Engine**:

1. **CLIP Semantic Features (Style, Fabric, Pattern):**
   We extract a 512-dimensional normalized CLIP embedding from the image. This captures the garment's texture, weave pattern complexity, and fabric semantics.
2. **Spatial Color Layout Grid (Color Distribution):**
   Sarees are highly defined by their colors, particularly the border, body, and pallu layout. To capture this spatial distribution, we resize the image to a small 8x8 grid, flatten it into a 192-dimensional vector, and normalize it. This represents the spatial color footprint of the saree.
3. **Multimodal Fusion Search:**
   If the user uploads an image *and* provides a text query (e.g., uploading a saree and typing "but in blue silk"), we compute:
   - Visual CLIP similarity ($\text{Similarity}_{\text{CLIP\_Img}}$)
   - Textual CLIP similarity ($\text{Similarity}_{\text{CLIP\_Text}}$)
   - Spatial Color layout similarity ($\text{Similarity}_{\text{Color}}$)
   We combine the CLIP scores (65% image, 35% text) and then apply the Style vs. Color sliders:
   $$\text{Score}_{\text{Base}} = w_{\text{style}} \cdot (0.65 \cdot \text{Similarity}_{\text{CLIP\_Img}} + 0.35 \cdot \text{Similarity}_{\text{CLIP\_Text}}) + w_{\text{color}} \cdot \text{Similarity}_{\text{Color}}$$
4. **Exact Keyword Boosting:**
   We filter out common conversational stopwords and extract core fashion keywords. If a candidate saree name matches keywords like *Silk*, *Organza*, or *Banarasi*, it receives a boost of $+0.08$ per keyword (up to $+0.24$ max) to ensure exact matches are ranked at the top.
   $$\text{Score}_{\text{Final}} = \min(\text{Score}_{\text{Base}} + \text{Boost}_{\text{Keywords}}, 1.0)$$

---

## 📦 Setup & Running Locally

### Prerequisites
- Python 3.9+
- A Google Gemini API Key

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository_url>
   cd TailorTalk
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   *Note: If you don't have `requirements.txt`, install manually:*
   ```bash
   pip install torch torchvision transformers faiss-cpu streamlit google-generativeai pillow numpy pandas requests
   ```

3. **Process and Index the Dataset:**
   Place your saree images in `data/images` and run the indexing script:
   ```bash
   python build_index.py
   ```
   This will read `saree_dataset.csv`, deduplicate product SKUs, extract embeddings, and generate the local FAISS index files:
   - `data/saree_index.pkl`
   - `data/clip_index.faiss`
   - `data/color_index.faiss`

4. **Verify the Installation:**
   ```bash
   python src/verify.py
   ```

5. **Start the Streamlit Application:**
   ```bash
   streamlit run app.py
   ```

---

## ☁️ Deployment

This application is designed to run out of the box on cloud hosting platforms such as **Streamlit Community Cloud** or **Hugging Face Spaces**:
- The 1,024 images (~100MB total) and pre-built index files are committed directly to the repository, removing any need for external image storage or databases.
- Reviewers can securely provide their `GEMINI_API_KEY` directly through the Streamlit sidebar field to interact with the conversational agent immediately.

---

## ⚖️ Assumptions & Trade-offs

1. **Local Embeddings on Cloud Deployment:**
   Running CLIP locally inside Streamlit Community Cloud or Hugging Face Spaces uses CPU inference. Since our dataset is small (649 unique products) and visual search is run on a single query image at a time, CPU inference is extremely fast (~1-2 seconds) and avoids the cost/complexity of GPU hosting.
2. **Local FAISS Index:**
   We chose local FAISS index files over cloud solutions like Pinecone or Qdrant. Because the dataset has 649 unique products, a local FAISS database is lightweight, has zero network latency, is completely free, and makes deployment 100% self-contained.
3. **Resolution of Spatial Color Grid:**
   We chose an 8x8 grid for color layouts. A smaller grid (4x4) is too coarse, while a larger grid (16x16) starts capturing micro-patterns (noise) instead of macro color regions like borders and body. 8x8 is the sweet spot for saree layouts.
4. **Deduplication by SKU:**
   The source CSV contained duplicate SKUs (e.g. mapping size variants or duplicate listings). We deduplicated the catalog to 649 unique SKUs to ensure the search gallery presents clean, unique product items instead of identical listings.

