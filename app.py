import os
import streamlit as st
import textwrap
import base64
from PIL import Image
from src.searcher import SareeSearchEngine
from src.agent import SareeAgent

# Set page configuration
st.set_page_config(
    page_title="TailorTalk | Luxury Saree Search Agent",
    page_icon="🏮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject custom CSS for premium fashion aesthetics (High-Fidelity Glassmorphism & Visual Animations)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@500;700;900&family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap');

    /* Hide Streamlit default headers/footers for total app immersion */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    [data-testid="stHeader"] {background: rgba(0,0,0,0) !important;}

    /* Main Layout with Luxury Animated Glow Background */
    .stApp {
        background: radial-gradient(circle at 10% 15%, rgba(212, 175, 55, 0.12) 0%, transparent 35%),
                    radial-gradient(circle at 90% 85%, rgba(186, 85, 211, 0.08) 0%, transparent 40%),
                    radial-gradient(circle at 50% 50%, rgba(212, 175, 55, 0.03) 0%, transparent 50%),
                    #050608 !important;
        color: #f3f4f6;
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    /* Scrollbars customization */
    ::-webkit-scrollbar {
        width: 6px;
        height: 6px;
    }
    ::-webkit-scrollbar-track {
        background: transparent;
    }
    ::-webkit-scrollbar-thumb {
        background: rgba(212, 175, 55, 0.25);
        border-radius: 10px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(212, 175, 55, 0.5);
    }
    
    /* Header and Titles */
    h1, h2, h3, .title-text {
        font-family: 'Cinzel', serif !important;
        background: linear-gradient(135deg, #ffe082, #d4af37, #aa7c11);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 900;
        letter-spacing: 1.5px;
        text-shadow: 0 0 40px rgba(212, 175, 55, 0.2);
    }
    
    /* Custom Luxury Hero Banner */
    .hero-banner {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.02), rgba(255, 255, 255, 0.005)) !important;
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(212, 175, 55, 0.25) !important;
        border-radius: 24px !important;
        padding: 30px !important;
        margin-bottom: 35px !important;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5), inset 0 0 30px rgba(212, 175, 55, 0.05) !important;
        position: relative;
        overflow: hidden;
    }
    .hero-banner::before {
        content: "";
        position: absolute;
        top: 0; left: 0; right: 0; height: 2px;
        background: linear-gradient(90deg, transparent, rgba(212, 175, 55, 0.8), transparent);
    }
    
    /* Panel Layout Design */
    .dashboard-panel {
        background: rgba(255, 255, 255, 0.015) !important;
        backdrop-filter: blur(15px);
        -webkit-backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        border-radius: 24px !important;
        padding: 24px !important;
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.3) !important;
        margin-bottom: 25px !important;
    }
    
    /* Custom Chat Container */
    .chat-container {
        max-height: 480px;
        overflow-y: auto;
        padding: 10px 5px;
        display: flex;
        flex-direction: column;
        gap: 20px;
        margin-bottom: 15px;
    }
    
    .chat-row {
        display: flex;
        width: 100%;
        animation: slideUpFade 0.45s cubic-bezier(0.16, 1, 0.3, 1);
    }
    @keyframes slideUpFade {
        from { opacity: 0; transform: translateY(15px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .user-row { justify-content: flex-end; }
    .assistant-row { justify-content: flex-start; }
    
    .chat-bubble {
        max-width: 82%;
        padding: 16px 20px;
        border-radius: 20px;
        font-size: 0.94rem;
        line-height: 1.5;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.35);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
    }
    .user-bubble {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.035), rgba(255, 255, 255, 0.01));
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-bottom-right-radius: 3px;
        color: #f3f4f6;
    }
    .assistant-bubble {
        background: linear-gradient(135deg, rgba(212, 175, 55, 0.06), rgba(212, 175, 55, 0.015));
        border: 1px solid rgba(212, 175, 55, 0.3);
        border-bottom-left-radius: 3px;
        color: #f4ebd0;
        box-shadow: 0 8px 30px rgba(212, 175, 55, 0.05);
    }
    .bubble-sender {
        font-size: 0.68rem;
        font-weight: 700;
        text-transform: uppercase;
        margin-bottom: 6px;
        letter-spacing: 1.5px;
    }
    .user-bubble .bubble-sender { color: #a1a1aa; }
    .assistant-bubble .bubble-sender { color: #ffe082; }
    
    /* Saree Glass Card */
    .saree-card {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.02), rgba(255, 255, 255, 0.005)) !important;
        backdrop-filter: blur(25px) saturate(180%) !important;
        -webkit-backdrop-filter: blur(25px) saturate(180%) !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        border-radius: 24px !important;
        padding: 0px !important;
        text-align: center !important;
        transition: all 0.5s cubic-bezier(0.16, 1, 0.3, 1) !important;
        margin-bottom: 25px !important;
        box-shadow: 0 15px 40px rgba(0, 0, 0, 0.4) !important;
        overflow: hidden !important;
        display: flex;
        flex-direction: column;
    }
    .saree-card:hover {
        transform: translateY(-10px) scale(1.02) !important;
        border-color: rgba(212, 175, 55, 0.4) !important;
        box-shadow: 0 20px 50px rgba(212, 175, 55, 0.18) !important;
        background: rgba(255, 255, 255, 0.03) !important;
    }
    
    .saree-img-container {
        width: 100%;
        height: 290px;
        overflow: hidden;
        position: relative;
        background: #0d0e11;
        border-bottom: 1px solid rgba(255, 255, 255, 0.04);
    }
    .saree-img {
        width: 100%;
        height: 100%;
        object-fit: cover;
        transition: transform 0.8s cubic-bezier(0.16, 1, 0.3, 1);
    }
    .saree-card:hover .saree-img {
        transform: scale(1.08);
    }
    
    .saree-details {
        padding: 20px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        flex-grow: 1;
        text-align: center;
        background: rgba(7, 8, 10, 0.2);
    }
    
    .saree-name {
        font-weight: 600;
        margin: 0;
        color: #f4ebd0;
        font-size: 0.94rem;
        line-height: 1.4;
        height: 2.8em;
        overflow: hidden;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        font-family: 'Cinzel', serif;
    }
    .saree-sku {
        margin: 5px 0 0 0;
        font-size: 0.7rem;
        color: #828290;
        letter-spacing: 0.8px;
        text-transform: uppercase;
    }
    
    /* Similarity Score Badge (Glassmorphic Gold) */
    .score-badge {
        background: rgba(212, 175, 55, 0.08) !important;
        backdrop-filter: blur(4px) !important;
        border: 1px solid rgba(212, 175, 55, 0.35) !important;
        color: #ffd54f !important;
        padding: 6px 14px !important;
        border-radius: 30px !important;
        font-weight: 600 !important;
        font-size: 0.75rem !important;
        display: inline-block;
        box-shadow: 0 4px 15px rgba(212, 175, 55, 0.05) !important;
    }
    
    /* Breakdown Scores */
    .breakdown-text {
        font-size: 0.7rem !important;
        color: #a1a1aa !important;
        margin-top: 6px !important;
        letter-spacing: 0.2px !important;
    }
    
    /* Premium Buy Button */
    .buy-button {
        display: inline-block !important;
        margin-top: 14px !important;
        background: linear-gradient(135deg, #aa7c11, #d4af37) !important;
        color: #07080a !important;
        padding: 8px 20px !important;
        border-radius: 8px !important;
        font-size: 0.78rem !important;
        font-weight: 700 !important;
        text-decoration: none !important;
        transition: all 0.35s cubic-bezier(0.16, 1, 0.3, 1) !important;
        box-shadow: 0 4px 15px rgba(212, 175, 55, 0.25) !important;
        border: none !important;
        letter-spacing: 0.5px;
    }
    .buy-button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(212, 175, 55, 0.45) !important;
        color: #000000 !important;
    }
    
    /* Form inputs custom styling */
    .stTextInput > div > div > input {
        background-color: rgba(255, 255, 255, 0.015) !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        border-radius: 12px !important;
        color: #f3f4f6 !important;
        backdrop-filter: blur(10px) !important;
        padding: 12px 16px !important;
        transition: all 0.3s ease !important;
    }
    .stTextInput > div > div > input:focus {
        border-color: rgba(212, 175, 55, 0.5) !important;
        box-shadow: 0 0 15px rgba(212, 175, 55, 0.15) !important;
        background-color: rgba(255, 255, 255, 0.03) !important;
    }
    
    /* File uploader customizing */
    [data-testid="stFileUploader"] {
        border: 1px dashed rgba(212, 175, 55, 0.3) !important;
        background: rgba(255, 255, 255, 0.01) !important;
        border-radius: 16px !important;
        padding: 16px !important;
        backdrop-filter: blur(5px) !important;
    }
    [data-testid="stFileUploader"]:hover {
        border-color: rgba(212, 175, 55, 0.7) !important;
        background: rgba(255, 255, 255, 0.02) !important;
    }
    
    /* Tabs custom styling */
    .stTabs [data-baseweb="tab-list"] {
        background-color: transparent !important;
        gap: 12px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.04) !important;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: rgba(255, 255, 255, 0.01) !important;
        border: 1px solid rgba(255, 255, 255, 0.04) !important;
        color: #a1a1aa !important;
        border-radius: 12px 12px 0 0 !important;
        padding: 10px 20px !important;
        transition: all 0.3s ease !important;
        font-family: 'Cinzel', serif !important;
        font-size: 0.8rem !important;
        letter-spacing: 0.5px;
    }
    .stTabs [data-baseweb="tab"]:hover {
        color: #f5d061 !important;
        border-color: rgba(212, 175, 55, 0.3) !important;
    }
    .stTabs [aria-selected="true"] {
        color: #07080a !important;
        background: linear-gradient(135deg, #ffe082, #d4af37) !important;
        border-color: transparent !important;
        font-weight: bold !important;
    }
    
    /* Action button customization */
    .stButton > button {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.03), rgba(255, 255, 255, 0.01)) !important;
        border: 1px solid rgba(212, 175, 55, 0.35) !important;
        color: #f5d061 !important;
        border-radius: 12px !important;
        padding: 10px 24px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        font-family: 'Cinzel', serif !important;
        letter-spacing: 1px;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #ffe082, #d4af37) !important;
        color: #07080a !important;
        border-color: transparent !important;
        box-shadow: 0 0 15px rgba(212, 175, 55, 0.3) !important;
        transform: translateY(-2px);
    }
    
    /* Sidebar glassmorphism */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, rgba(13, 14, 18, 0.85) 0%, rgba(7, 8, 10, 0.95) 100%) !important;
        backdrop-filter: blur(25px) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.03) !important;
        box-shadow: 5px 0 35px rgba(0, 0, 0, 0.5) !important;
    }
    .stSlider > label {
        color: #f5d061 !important;
        font-family: 'Cinzel', serif !important;
        font-size: 0.85rem !important;
        font-weight: 600 !important;
    }
    
    /* General streamlit layouts container hiding borders */
    [data-testid="stForm"] {
        border: none !important;
        background: transparent !important;
    }
    hr {
        border-color: rgba(212, 175, 55, 0.12) !important;
    }
</style>
""", unsafe_allow_html=True)

# Helper function to save uploaded file
def save_uploaded_file(uploaded_file):
    try:
        os.makedirs("data", exist_ok=True)
        temp_path = "data/temp_query.jpg"
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        return temp_path
    except Exception as e:
        st.error(f"Error saving uploaded image: {e}")
        return None

# Saree attributes tag extractor
def get_saree_tags(title):
    title_lower = str(title).lower()
    tags = []
    if "silk" in title_lower:
        tags.append(("Silk", "#e6b325"))
    if "organza" in title_lower:
        tags.append(("Organza", "#da70d6"))
    if "crape" in title_lower or "crepe" in title_lower:
        tags.append(("Crepe", "#ff7f50"))
    if "tissue" in title_lower:
        tags.append(("Tissue", "#40e0d0"))
    if "pashmina" in title_lower:
        tags.append(("Pashmina", "#ff69b4"))
    if "banarasi" in title_lower:
        tags.append(("Banarasi", "#8a2be2"))
    if "munga" in title_lower:
        tags.append(("Munga", "#4682b4"))
    if "floral" in title_lower:
        tags.append(("Floral", "#2e8b57"))
    if not tags:
        tags.append(("Traditional", "#7f8c8d"))
    return tags[:3]

# Load the search engine (cached to run once)
@st.cache_resource
def load_search_engine():
    try:
        return SareeSearchEngine()
    except Exception as e:
        st.error(f"Error loading search engine: {e}. Did you run indexing (build_index.py)?")
        return None

# Main App Header (Luxury Glassmorphic Hero Banner)
st.markdown("""
<div class="hero-banner">
    <div style="display: flex; align-items: center; gap: 15px;">
        <span style="font-size: 2.2rem; filter: drop-shadow(0 0 10px rgba(212,175,55,0.4));">🏮</span>
        <h1 style="margin: 0; font-size: 2.3rem;">TailorTalk</h1>
    </div>
    <p style="margin: 10px 0 0 0; color: #a1a1aa; font-size: 0.96rem; line-height: 1.5; font-family: 'Plus Jakarta Sans', sans-serif;">
        Experience the future of Indian fashion discovery. Upload a design or describe your styling preferences, and our conversational AI agent will query a fine-grained vector catalogue of sarees to find visual and semantic matches instantly.
    </p>
</div>
""", unsafe_allow_html=True)

# Initialize Session State variables
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Namaste! I am TailorTalk. Upload a saree image or describe what you're looking for, and I'll find the perfect match from our catalogue."}
    ]
if "search_results" not in st.session_state:
    st.session_state.search_results = None
if "current_image_path" not in st.session_state:
    st.session_state.current_image_path = None

# Sidebar Configuration
st.sidebar.image("https://img.icons8.com/color/96/saree.png", width=80)
st.sidebar.header("Agent Settings")

# API Key Configuration
api_key = os.environ.get("GEMINI_API_KEY", "")
if not api_key:
    api_key = st.sidebar.text_input("Gemini API Key", type="password", help="Enter your Gemini API key to enable the conversational agent.")
else:
    st.sidebar.markdown("""<div style="background: rgba(230, 179, 37, 0.08); border: 1px solid rgba(230, 179, 37, 0.35); border-radius: 8px; padding: 10px 14px; margin-bottom: 15px;">
<span style="color: #f5d061; font-size: 0.82rem; font-weight: 600; display: block; text-align: center;">🤖 Agent Status: Active ✨</span>
</div>""", unsafe_allow_html=True)

# Search Weights Setup
st.sidebar.subheader("Similarity Weights")
w_clip = st.sidebar.slider("Style Weight (CLIP features)", 0.0, 1.0, 0.7, 0.05, 
                           help="Focus on textile weave, fabric texture, and pattern complexity.")
w_color = st.sidebar.slider("Color Weight (Color grid)", 0.0, 1.0, 0.3, 0.05,
                            help="Focus strictly on the spatial color distribution (borders, body, pallu).")

# Normalize weights
weight_sum = w_clip + w_color
if weight_sum > 0:
    w_clip_norm = w_clip / weight_sum
    w_color_norm = w_color / weight_sum
else:
    w_clip_norm, w_color_norm = 0.5, 0.5

st.sidebar.caption(f"Normalized Weights: Style: {w_clip_norm:.2f} | Color: {w_color_norm:.2f}")

# Limit matches
limit_matches = st.sidebar.slider("Number of Matches", 1, 10, 5)

# Clear chat button
if st.sidebar.button("Clear Chat History", use_container_width=True):
    st.session_state.messages = [
        {"role": "assistant", "content": "Namaste! Chat history cleared. How can I assist you today?"}
    ]
    st.session_state.search_results = None
    st.session_state.current_image_path = None
    if os.path.exists("data/temp_query.jpg"):
        try:
            os.remove("data/temp_query.jpg")
        except:
            pass
    st.rerun()

# Load visual search engine
search_engine = load_search_engine()

# Main Application Layout: Two Columns with panels
col_chat, col_results = st.columns([1, 1], gap="large")

# Right Column: Visual Similarity Search Results
with col_results:
    st.markdown("""<div class="dashboard-panel">
<h2 style="font-family: 'Cinzel', serif; font-size: 1.4rem; margin: 0; color: #ffe082; display: flex; align-items: center; gap: 10px;">🛍️ Visual Search Gallery</h2>
<p style="font-size: 0.82rem; color: #888; margin: 5px 0 0 0;">Upload design images or image links to discover visual and color matches.</p>
</div>""", unsafe_allow_html=True)
    
    # Image Input section (Upload or link)
    img_tab_upload, img_tab_url = st.tabs(["Upload Image", "Image URL"])
    
    query_image = None
    
    with img_tab_upload:
        uploaded_file = st.file_uploader("Upload a saree image...", type=["jpg", "jpeg", "png"])
        if uploaded_file is not None:
            temp_path = save_uploaded_file(uploaded_file)
            st.session_state.current_image_path = temp_path
            try:
                query_image = Image.open(uploaded_file)
                st.image(query_image, caption="Uploaded Saree Query", width=180)
            except Exception as e:
                st.error(f"Invalid image file: {e}")
                
    with img_tab_url:
        image_url = st.text_input("Or paste an image URL...")
        if image_url:
            import requests
            from io import BytesIO
            try:
                response = requests.get(image_url, timeout=10)
                query_image = Image.open(BytesIO(response.content))
                os.makedirs("data", exist_ok=True)
                temp_path = "data/temp_query.jpg"
                query_image.save(temp_path)
                st.session_state.current_image_path = temp_path
                st.image(query_image, caption="Image URL Query", width=180)
            except Exception as e:
                st.error(f"Failed to load image from URL: {e}")
                
    # Visual Search Action Button (Standalone search without agent)
    if st.button("Run Visual Search", use_container_width=True):
        if query_image is not None and search_engine is not None:
            with st.spinner("Searching matching sarees..."):
                results = search_engine.search(
                    query_image=query_image,
                    top_k=limit_matches,
                    w_clip=w_clip_norm,
                    w_color=w_color_norm
                )
                st.session_state.search_results = results
        elif query_image is None:
            st.warning("Please upload an image or provide a valid URL first.")
            
    st.markdown("---")
    
    # Display Search Results
    if st.session_state.search_results:
        st.markdown(f"#### Top {len(st.session_state.search_results)} Matches")
        
        # Display in grid (2 items per row)
        cols = st.columns(2)
        for idx, item in enumerate(st.session_state.search_results):
            col = cols[idx % 2]
            with col:
                # Load saree image as base64 for seamless embedding
                img_path = item["relative_path"]
                img_html = ""
                if os.path.exists(img_path):
                    try:
                        with open(img_path, "rb") as img_file:
                            img_base64 = base64.b64encode(img_file.read()).decode('utf-8')
                        img_html = f'<div class="saree-img-container"><img src="data:image/webp;base64,{img_base64}" class="saree-img"/></div>'
                    except Exception:
                        img_html = ""
                    
                # Format price details
                price_html = ""
                if item.get("discounted_price") and item.get("retail_price"):
                    price_html = f"""<p style="margin: 5px 0 0 0; font-size: 0.9rem;">
<span style="color: #ffd54f; font-weight: bold;">₹{item['discounted_price']}</span>
<span style="text-decoration: line-through; color: #71717a; font-size: 0.8rem; margin-left: 5px;">₹{item['retail_price']}</span>
</p>"""
                elif item.get("discounted_price"):
                    price_html = f'<p style="margin: 5px 0 0 0; font-size: 0.9rem; color: #ffd54f; font-weight: bold;">₹{item["discounted_price"]}</p>'
                
                # Buy Now link
                buy_button_html = ""
                if item.get("website_link"):
                    buy_button_html = f"""<div style="margin-top: 10px;">
<a href="{item['website_link']}" target="_blank" class="buy-button">Buy Now ↗</a>
</div>"""

                # Get visual tags
                tags = get_saree_tags(item.get('name', ''))
                tags_html = '<div style="display: flex; gap: 5px; justify-content: center; flex-wrap: wrap; margin-top: 6px;">'
                for tag_name, color in tags:
                    tags_html += f'<span style="background-color: {color}15; border: 1px solid {color}40; color: {color}; padding: 2px 8px; border-radius: 4px; font-size: 0.68rem; font-weight: 600;">{tag_name}</span>'
                tags_html += '</div>'

                card_html = f"""<div class="saree-card">
{img_html}
<div class="saree-details">
<p class="saree-name">{item.get('name', item['filename'])}</p>
<p class="saree-sku">SKU: {item.get('sku', item['filename'])}</p>
{tags_html}
{price_html}
<div style="margin-top: 10px;">
<span class="score-badge">Match: {item['score']*100:.1f}%</span>
</div>
<div class="breakdown-text">Style: {item['clip_score']*100:.1f}% | Color: {item['color_score']*100:.1f}%</div>
{buy_button_html}
</div>
</div>"""
                st.markdown(card_html, unsafe_allow_html=True)
    else:
        st.info("No active search results. Perform a Visual Search or chat with the agent to populate this gallery.")

# Left Column: Chat Assistant
with col_chat:
    st.markdown("""<div class="dashboard-panel">
<h2 style="font-family: 'Cinzel', serif; font-size: 1.4rem; margin: 0; color: #ffe082; display: flex; align-items: center; gap: 10px;">💬 Conversational Assistant</h2>
<p style="font-size: 0.82rem; color: #888; margin: 5px 0 0 0;">Talk to TailorTalk to describe styling requests, get match reviews, or query sarees.</p>
</div>""", unsafe_allow_html=True)
    
    # Custom HTML Chat Log Renderer
    chat_html = '<div class="chat-container">'
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            chat_html += f"""
            <div class="chat-row user-row">
                <div class="chat-bubble user-bubble">
                    <div class="bubble-sender">You</div>
                    <div class="bubble-content">{msg['content']}</div>
                </div>
            </div>
            """
        else:
            chat_html += f"""
            <div class="chat-row assistant-row">
                <div class="chat-bubble assistant-bubble">
                    <div class="bubble-sender">TailorTalk AI ✨</div>
                    <div class="bubble-content">{msg['content']}</div>
                </div>
            </div>
            """
    chat_html += '</div>'
    st.markdown(chat_html, unsafe_allow_html=True)
            
    # Check if Agent API key is present
    if not api_key:
        st.warning("Please enter your Gemini API Key in the sidebar to enable natural conversation and agent tools.")
        st.stop()
        
    # Instantiate agent
    if search_engine is not None:
        agent = SareeAgent(api_key=api_key, search_engine=search_engine)
    else:
        agent = None
        st.error("Search engine is not loaded. Indexing is required.")
        
    # Chat Input
    if agent is not None:
        user_input = st.chat_input("Ask TailorTalk (e.g. 'Show me pink sarees with gold borders' or 'Find traditional silk sarees')")
        
        if user_input:
            # 1. Display user message
            st.session_state.messages.append({"role": "user", "content": user_input})
            
            # 2. Run agent response
            with st.spinner("TailorTalk is thinking..."):
                try:
                    img_path_query = st.session_state.current_image_path if st.session_state.current_image_path else None
                    
                    response = agent.run_chat(
                        messages_history=st.session_state.messages[:-1],
                        user_message=user_input,
                        temp_image_path=img_path_query
                    )
                    
                    # If the agent called the visual search tool behind the scenes, update UI results
                    if response["tool_called"] and response["tool_results"]:
                        st.session_state.search_results = response["tool_results"]
                        
                    # Save assistant response
                    st.session_state.messages.append({"role": "assistant", "content": response["response_text"]})
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"Agent error: {e}")
