import os
import streamlit as st
import textwrap
import base64
from PIL import Image
from src.searcher import SareeSearchEngine
from src.agent import SareeAgent

# Set page configuration
st.set_page_config(
    page_title="TailorTalk | Luxury AI Saree Stylist",
    page_icon="🏮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject custom CSS to replicate the high-end plum/rose-gold luxury design
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;500;700;900&family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap');

    /* Hide Streamlit default UI components */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    [data-testid="stHeader"] {background: rgba(0,0,0,0) !important;}

    /* Premium Color Scheme and Background */
    .stApp {
        background: radial-gradient(circle at 15% 20%, rgba(176, 62, 122, 0.15) 0%, transparent 40%),
                    radial-gradient(circle at 85% 80%, rgba(212, 175, 55, 0.08) 0%, transparent 40%),
                    radial-gradient(circle at 50% 50%, rgba(176, 62, 122, 0.04) 0%, transparent 60%),
                    #0e030a !important;
        color: #f3f4f6;
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    /* Scrollbars */
    ::-webkit-scrollbar {
        width: 6px;
        height: 6px;
    }
    ::-webkit-scrollbar-track {
        background: transparent;
    }
    ::-webkit-scrollbar-thumb {
        background: rgba(176, 62, 122, 0.3);
        border-radius: 10px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(212, 175, 55, 0.4);
    }
    
    /* Typography */
    h1, h2, h3, .title-text {
        font-family: 'Cinzel', serif !important;
        background: linear-gradient(135deg, #ffe082, #d4af37, #aa7c11);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700;
        letter-spacing: 0.5px;
    }
    
    /* Hero Banner Container */
    .hero-container {
        background: linear-gradient(135deg, rgba(35, 10, 26, 0.65), rgba(20, 5, 15, 0.85)) !important;
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(176, 62, 122, 0.25) !important;
        border-radius: 28px !important;
        padding: 30px !important;
        margin-bottom: 30px !important;
        box-shadow: 0 20px 50px rgba(0, 0, 0, 0.6) !important;
        display: flex;
        flex-wrap: wrap;
        justify-content: space-between;
        align-items: center;
        gap: 30px;
    }
    
    /* Segmented Header Cards */
    .header-card-grid {
        display: flex;
        gap: 20px;
        flex-wrap: wrap;
        flex-grow: 1;
        justify-content: flex-end;
    }
    .header-feature-card {
        background: rgba(255, 255, 255, 0.02) !important;
        border: 1px solid rgba(255, 255, 255, 0.04) !important;
        padding: 16px 20px !important;
        border-radius: 16px !important;
        backdrop-filter: blur(10px) !important;
        width: 220px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.2) !important;
    }
    .feature-title {
        color: #f4ebd0 !important;
        font-family: 'Cinzel', serif !important;
        font-size: 0.88rem !important;
        font-weight: bold !important;
        margin: 5px 0 2px 0 !important;
    }
    .feature-desc {
        color: #a1a1aa !important;
        font-size: 0.78rem !important;
        line-height: 1.3 !important;
    }
    
    /* Panel Layout styling */
    .stpanel {
        background: rgba(26, 6, 20, 0.45) !important;
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(176, 62, 122, 0.15) !important;
        border-radius: 24px !important;
        padding: 24px !important;
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.4) !important;
        margin-bottom: 25px !important;
    }
    
    /* Title Icons */
    .panel-title {
        font-family: 'Cinzel', serif !important;
        font-size: 1.3rem !important;
        color: #f3ebd0 !important;
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 8px;
    }
    
    /* Suggestion Chips */
    .chip-container {
        display: flex;
        gap: 8px;
        flex-wrap: wrap;
        margin-top: 12px;
        margin-bottom: 12px;
    }
    .suggestion-chip {
        background: rgba(176, 62, 122, 0.08) !important;
        border: 1px solid rgba(176, 62, 122, 0.25) !important;
        color: #f4ebd0 !important;
        padding: 6px 14px !important;
        border-radius: 30px !important;
        font-size: 0.76rem !important;
        font-weight: 500 !important;
        cursor: pointer;
        transition: all 0.3s ease !important;
    }
    .suggestion-chip:hover {
        background: rgba(176, 62, 122, 0.2) !important;
        border-color: rgba(212, 175, 55, 0.4) !important;
        transform: translateY(-1px);
    }
    
    /* Chat display */
    .chat-display {
        max-height: 400px;
        overflow-y: auto;
        padding: 10px 5px;
        display: flex;
        flex-direction: column;
        gap: 16px;
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
        border-radius: 24px;
        font-size: 0.94rem;
        line-height: 1.5;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.35);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
    }
    .user-bubble {
        background: rgba(255, 255, 255, 0.02) ;
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-bottom-right-radius: 4px;
        color: #f3f4f6;
    }
    .assistant-bubble {
        background: rgba(176, 62, 122, 0.04);
        border: 1px solid rgba(176, 62, 122, 0.25);
        border-bottom-left-radius: 4px;
        color: #f4ebd0;
        display: flex;
        gap: 15px;
        align-items: flex-start;
    }
    .monogram-avatar {
        background: linear-gradient(135deg, #aa7c11, #d4af37);
        color: #0e030a;
        width: 38px;
        height: 38px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-family: 'Cinzel', serif;
        font-weight: 900;
        font-size: 1.1rem;
        box-shadow: 0 4px 12px rgba(212,175,55,0.3);
        flex-shrink: 0;
    }
    .bubble-inner-content {
        display: flex;
        flex-direction: column;
    }
    
    /* Custom Saree Image Card */
    .saree-card {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.02), rgba(255, 255, 255, 0.005)) !important;
        backdrop-filter: blur(25px) saturate(180%) !important;
        -webkit-backdrop-filter: blur(25px) saturate(180%) !important;
        border: 1px solid rgba(176, 62, 122, 0.15) !important;
        border-radius: 28px !important;
        padding: 0px !important;
        text-align: center !important;
        transition: all 0.5s cubic-bezier(0.16, 1, 0.3, 1) !important;
        margin-bottom: 25px !important;
        box-shadow: 0 15px 40px rgba(0, 0, 0, 0.45) !important;
        overflow: hidden !important;
        display: flex;
        flex-direction: column;
    }
    .saree-card:hover {
        transform: translateY(-10px) scale(1.02) !important;
        border-color: rgba(212, 175, 55, 0.4) !important;
        box-shadow: 0 20px 50px rgba(212, 175, 55, 0.22) !important;
        background: rgba(255, 255, 255, 0.035) !important;
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
    .score-badge {
        background: rgba(212, 175, 55, 0.07) !important;
        backdrop-filter: blur(4px) !important;
        border: 1px solid rgba(212, 175, 55, 0.35) !important;
        color: #ffd54f !important;
        padding: 6px 16px !important;
        border-radius: 30px !important;
        font-weight: 600 !important;
        font-size: 0.75rem !important;
        display: inline-block;
        box-shadow: 0 4px 15px rgba(212, 175, 55, 0.05) !important;
    }
    .breakdown-text {
        font-size: 0.7rem !important;
        color: #a1a1aa !important;
        margin-top: 6px !important;
        letter-spacing: 0.2px !important;
    }
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
    }
    .buy-button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(212, 175, 55, 0.45) !important;
        color: #000000 !important;
    }
    
    /* File Uploader styling */
    [data-testid="stFileUploader"] {
        border: 1px dashed rgba(176, 62, 122, 0.35) !important;
        background: rgba(255, 255, 255, 0.008) !important;
        border-radius: 20px !important;
        padding: 24px !important;
        transition: all 0.3s ease !important;
    }
    [data-testid="stFileUploader"]:hover {
        border-color: rgba(212, 175, 55, 0.5) !important;
        background: rgba(255, 255, 255, 0.015) !important;
    }
    
    /* Custom Tabs */
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
    }
    .stTabs [data-baseweb="tab"]:hover {
        color: #ffe082 !important;
        border-color: rgba(176, 62, 122, 0.3) !important;
    }
    .stTabs [aria-selected="true"] {
        color: #ffffff !important;
        background: linear-gradient(135deg, rgba(176, 62, 122, 0.6), rgba(176, 62, 122, 0.3)) !important;
        border: 1px solid rgba(176, 62, 122, 0.5) !important;
        font-weight: bold !important;
    }
    
    /* High-End Glowing Search Button */
    .stButton > button {
        background: linear-gradient(90deg, #a73a6c 0%, #e28e57 100%) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 14px !important;
        padding: 12px 28px !important;
        font-weight: bold !important;
        font-family: 'Cinzel', serif !important;
        letter-spacing: 1px;
        font-size: 0.88rem !important;
        transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1) !important;
        box-shadow: 0 6px 20px rgba(176, 62, 122, 0.35) !important;
        width: 100% !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 10px 30px rgba(176, 62, 122, 0.6) !important;
        filter: brightness(1.1);
    }
    
    /* Form input styling */
    .stTextInput > div > div > input {
        background-color: rgba(255, 255, 255, 0.015) !important;
        border: 1px solid rgba(255, 255, 255, 0.06) !important;
        border-radius: 14px !important;
        color: #f3f4f6 !important;
        backdrop-filter: blur(10px) !important;
        padding: 12px 18px !important;
    }
    .stTextInput > div > div > input:focus {
        border-color: rgba(176, 62, 122, 0.6) !important;
        box-shadow: 0 0 15px rgba(176, 62, 122, 0.25) !important;
    }
    
    /* Sidebar glassmorphism */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, rgba(20, 5, 15, 0.9) 0%, rgba(10, 2, 7, 0.98) 100%) !important;
        backdrop-filter: blur(25px) !important;
        border-right: 1px solid rgba(176, 62, 122, 0.12) !important;
        box-shadow: 5px 0 35px rgba(0, 0, 0, 0.6) !important;
    }
    .stSlider > label {
        color: #f5d061 !important;
        font-family: 'Cinzel', serif !important;
        font-size: 0.85rem !important;
    }
    
    /* Value proposition footer bar */
    .trust-footer-bar {
        background: linear-gradient(90deg, rgba(35, 10, 26, 0.7), rgba(20, 5, 15, 0.9)) !important;
        backdrop-filter: blur(15px);
        -webkit-backdrop-filter: blur(15px);
        border: 1px solid rgba(176, 62, 122, 0.2) !important;
        border-radius: 20px !important;
        padding: 18px 30px !important;
        margin-top: 40px !important;
        margin-bottom: 20px !important;
        display: flex;
        justify-content: space-around;
        align-items: center;
        flex-wrap: wrap;
        gap: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.4) !important;
    }
    .trust-item {
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .trust-title {
        font-family: 'Cinzel', serif;
        font-size: 0.84rem;
        color: #f4ebd0;
        font-weight: bold;
        margin: 0;
    }
    .trust-desc {
        font-size: 0.72rem;
        color: #828290;
        margin: 0;
    }
    
    [data-testid="stForm"] {
        border: none !important;
        background: transparent !important;
    }
    hr {
        border-color: rgba(176, 62, 122, 0.15) !important;
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

# Main App Header (Luxury Glassmorphic Hero Banner matching Figma design)
st.markdown("""<div class="hero-container">
<div style="flex: 1; min-width: 320px; display: flex; align-items: center; gap: 20px;">
<!-- Vector Hanging Lanterns & Silhouette SVG Decoration -->
<svg width="60" height="70" viewBox="0 0 60 70" fill="none" xmlns="http://www.w3.org/2000/svg" style="opacity: 0.95; filter: drop-shadow(0 0 10px rgba(212,175,55,0.4));">
<line x1="12" y1="0" x2="12" y2="40" stroke="#d4af37" stroke-width="1.5"/>
<path d="M6 40C6 36.6863 8.68629 34 12 34C15.3137 34 18 36.6863 18 40V50C18 53.3137 15.3137 56 12 56C8.68629 56 6 53.3137 6 50V40Z" fill="#aa7c11" stroke="#ffe082" stroke-width="1"/>
<path d="M12 56V65" stroke="#ffe082" stroke-width="1"/>
<circle cx="12" cy="65" r="2" fill="#ffe082"/>
<line x1="42" y1="0" x2="42" y2="25" stroke="#d4af37" stroke-width="1.5"/>
<path d="M36 25C36 21.6863 38.6863 19 42 19C45.3137 19 48 21.6863 48 25V35C48 38.3137 45.3137 41 42 41C38.6863 41 36 38.3137 36 35V25Z" fill="#aa7c11" stroke="#ffe082" stroke-width="1"/>
<path d="M42 41V50" stroke="#ffe082" stroke-width="1"/>
<circle cx="42" cy="50" r="1.5" fill="#ffe082"/>
</svg>
<div>
<h1 style="margin: 0; font-size: 2.8rem; line-height: 1.1;">TailorTalk</h1>
<p style="margin: 5px 0 0 0; color: #ffd54f; font-family: 'Cinzel', serif; font-size: 0.88rem; letter-spacing: 1px; font-weight: 500;">Your AI Stylist for Timeless Saree Elegance</p>
</div>
</div>
<div class="header-card-grid">
<div class="header-feature-card">
<span style="font-size: 1.1rem;">✨</span>
<div class="feature-title">AI-Powered</div>
<div class="feature-desc">Smart understanding of your fashion style</div>
</div>
<div class="header-feature-card">
<span style="font-size: 1.1rem;">⚡</span>
<div class="feature-title">Instant Matches</div>
<div class="feature-desc">Find perfect sarees in a few seconds</div>
</div>
<div class="header-feature-card">
<span style="font-size: 1.1rem;">🎨</span>
<div class="feature-title">Curated Catalog</div>
<div class="feature-desc">Premium sarees from trusted artisans</div>
</div>
</div>
</div>""", unsafe_allow_html=True)


# Initialize Session State variables
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Namaste! I am TailorTalk, your AI fashion stylist. Tell me what kind of saree you're looking for, or upload an image to find visually matching designs!"}
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
limit_matches = st.sidebar.slider("Number of Matches", 1, 10, 6)

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

# Main Application Layout: Two Columns
col_chat, col_results = st.columns([1, 1], gap="large")

# Left Column: Conversational Assistant
with col_chat:
    st.markdown("""
    <div class="panel-title">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#d4af37" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
        </svg>
        <span>Conversational Assistant</span>
    </div>
    <p style="font-size: 0.84rem; color: #8c828e; margin: -5px 0 15px 0;">
        Describe what you're looking for, or upload an image and ask for style variations.
    </p>
    """, unsafe_allow_html=True)
    
    # Suggestion Chips
    st.markdown("<span style='font-size: 0.76rem; color: #a1a1aa; font-family: Cinzel;'>Try asking:</span>", unsafe_allow_html=True)
    st.markdown("""<div class="chip-container">
        <span class="suggestion-chip">Pink saree with gold border</span>
        <span class="suggestion-chip">Silk saree for wedding</span>
        <span class="suggestion-chip">Traditional Kanjeevaram</span>
        <span class="suggestion-chip">Cotton saree for summer</span>
    </div>""", unsafe_allow_html=True)

    # Custom HTML Chat Log Renderer
    chat_html = '<div class="chat-display">'
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
                    <div class="monogram-avatar">T</div>
                    <div class="bubble-inner-content">
                        <div class="bubble-sender">TailorTalk AI ✨</div>
                        <div class="bubble-content">{msg['content']}</div>
                    </div>
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
        user_input = st.chat_input("Describe your dream saree...")
        
        if user_input:
            st.session_state.messages.append({"role": "user", "content": user_input})
            
            with st.spinner("TailorTalk is thinking..."):
                try:
                    img_path_query = st.session_state.current_image_path if st.session_state.current_image_path else None
                    
                    response = agent.run_chat(
                        messages_history=st.session_state.messages[:-1],
                        user_message=user_input,
                        temp_image_path=img_path_query
                    )
                    
                    if response["tool_called"] and response["tool_results"]:
                        st.session_state.search_results = response["tool_results"]
                        
                    st.session_state.messages.append({"role": "assistant", "content": response["response_text"]})
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"Agent error: {e}")

# Right Column: Visual Search Gallery
with col_results:
    st.markdown("""
    <div class="panel-title">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#d4af37" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
            <circle cx="8.5" cy="8.5" r="1.5"></circle>
            <polyline points="21 15 16 10 5 21"></polyline>
        </svg>
        <span>Visual Search Gallery</span>
    </div>
    <p style="font-size: 0.84rem; color: #8c828e; margin: -5px 0 15px 0;">
        Upload a design image or paste any image URL to discover similar sarees from our collection.
    </p>
    """, unsafe_allow_html=True)
    
    # Image Input section (Upload or link)
    img_tab_upload, img_tab_url = st.tabs(["Upload Image", "Image URL"])
    
    query_image = None
    
    with img_tab_upload:
        # Custom structured drag and drop upload field
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
    if st.button("Run Visual Search"):
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

# Value Proposition Trust Footer Bar
st.markdown("""
<div class="trust-footer-bar">
    <div class="trust-item">
        <span style="font-size: 1.3rem;">🏺</span>
        <div>
            <div class="trust-title">1000+ Premium Sarees</div>
            <div class="trust-desc">Curated catalog of pure silk and organza</div>
        </div>
    </div>
    <div class="trust-item">
        <span style="font-size: 1.3rem;">🧑‍🎨</span>
        <div>
            <div class="trust-title">Trusted Artisans</div>
            <div class="trust-desc">Authentic handloom craftsmanship</div>
        </div>
    </div>
    <div class="trust-item">
        <span style="font-size: 1.3rem;">🛡️</span>
        <div>
            <div class="trust-title">Secure & Private</div>
            <div class="trust-desc">Your personal style data is protected</div>
        </div>
    </div>
    <div class="trust-item">
        <span style="font-size: 1.3rem;">🤖</span>
        <div>
            <div class="trust-title">24/7 AI Assistant</div>
            <div class="trust-desc">Always here to help you style</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)
