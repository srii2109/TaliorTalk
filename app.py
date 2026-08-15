import os
import base64
import requests
from io import BytesIO
import streamlit as st
from PIL import Image
from src.searcher import SareeSearchEngine
from src.agent import SareeAgent

st.set_page_config(
    page_title="TailorTalk | Luxury AI Saree Stylist",
    page_icon="🏮",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600;700;900&family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap');

#MainMenu, footer, header, [data-testid="stHeader"] { visibility: hidden; }

/* ─── Background ─── */
.stApp {
    background:
        radial-gradient(ellipse 60% 40% at 5% 10%,  rgba(180,50,110,0.18) 0%, transparent 60%),
        radial-gradient(ellipse 50% 50% at 95% 90%,  rgba(212,175,55,0.10) 0%, transparent 60%),
        radial-gradient(ellipse 80% 60% at 50% 50%,  rgba(100,15,60,0.12) 0%, transparent 70%),
        #090408;
    font-family: 'Plus Jakarta Sans', sans-serif;
    color: #f3f4f6;
}

::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-thumb { background: rgba(180,50,110,0.35); border-radius: 10px; }

/* ─── Hero Banner ─── */
.hero-banner {
    position: relative;
    overflow: hidden;
    background: linear-gradient(120deg, rgba(60,8,35,0.75) 0%, rgba(20,4,14,0.90) 100%);
    border: 1px solid rgba(212,175,55,0.20);
    border-radius: 28px;
    padding: 32px 36px;
    margin-bottom: 28px;
    box-shadow: 0 25px 60px rgba(0,0,0,0.6), inset 0 1px 0 rgba(212,175,55,0.15);
}
.hero-banner::before {
    content: '';
    position: absolute; top: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg, transparent 0%, rgba(212,175,55,0.9) 40%, rgba(180,50,110,0.7) 70%, transparent 100%);
}
.hero-banner::after {
    content: '';
    position: absolute; bottom: 0; left: 0; right: 0; height: 1px;
    background: linear-gradient(90deg, transparent, rgba(212,175,55,0.3), transparent);
}
.hero-inner {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 30px;
    flex-wrap: wrap;
}
.hero-brand { display: flex; align-items: center; gap: 20px; }
.hero-title {
    font-family: 'Cinzel', serif;
    font-size: 3rem;
    font-weight: 900;
    background: linear-gradient(135deg, #ffe082 0%, #d4af37 50%, #aa7c11 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0; line-height: 1;
    letter-spacing: 2px;
    text-shadow: none;
    white-space: nowrap;
}
.hero-sub {
    font-family: 'Cinzel', serif;
    color: #ffd54f;
    font-size: 0.82rem;
    letter-spacing: 1.5px;
    margin-top: 6px;
    opacity: 0.85;
}
.hero-description {
    color: #c4b5c4;
    font-size: 0.9rem;
    line-height: 1.6;
    max-width: 340px;
}
.feature-pills {
    display: flex;
    gap: 12px;
    flex-wrap: wrap;
    align-items: flex-start;
}
.feature-pill {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(212,175,55,0.18);
    border-radius: 18px;
    padding: 14px 18px;
    min-width: 130px;
    backdrop-filter: blur(8px);
    transition: all 0.3s ease;
}
.feature-pill:hover {
    border-color: rgba(212,175,55,0.5);
    background: rgba(212,175,55,0.05);
    transform: translateY(-3px);
    box-shadow: 0 8px 25px rgba(212,175,55,0.1);
}
.pill-icon { font-size: 1.2rem; margin-bottom: 6px; }
.pill-title {
    font-family: 'Cinzel', serif;
    font-size: 0.78rem;
    font-weight: 700;
    color: #f4ebd0;
    letter-spacing: 0.5px;
}
.pill-desc { font-size: 0.7rem; color: #888; margin-top: 2px; line-height: 1.3; }

/* ─── Panel ─── */
.panel {
    background: linear-gradient(140deg, rgba(40,8,28,0.6) 0%, rgba(15,4,11,0.8) 100%);
    border: 1px solid rgba(180,50,110,0.15);
    border-radius: 24px;
    padding: 26px;
    backdrop-filter: blur(16px);
    box-shadow: 0 20px 50px rgba(0,0,0,0.45);
    margin-bottom: 20px;
    position: relative;
    overflow: hidden;
}
.panel::before {
    content:'';
    position:absolute; top:0; left:0; right:0; height:1px;
    background: linear-gradient(90deg, transparent, rgba(212,175,55,0.5), transparent);
}
.panel-title {
    font-family: 'Cinzel', serif;
    font-size: 1.2rem;
    color: #f4ebd0;
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 6px;
    font-weight: 700;
}
.panel-desc { font-size: 0.82rem; color: #7a6a7a; margin-bottom: 18px; }

/* ─── Chips ─── */
.chips { display: flex; flex-wrap: wrap; gap: 8px; margin: 10px 0 16px; }
.chip {
    background: rgba(180,50,110,0.08);
    border: 1px solid rgba(180,50,110,0.28);
    color: #e8d5e8;
    padding: 6px 14px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.25s ease;
    display: inline-block;
}
.chip:hover {
    background: rgba(180,50,110,0.2);
    border-color: rgba(212,175,55,0.5);
    color: #ffd54f;
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(180,50,110,0.2);
}
.chip-label { font-size: 0.7rem; color: #7a6a7a; margin-bottom: 6px; font-family: 'Cinzel', serif; letter-spacing: 0.5px; }

/* ─── Chat Bubbles ─── */
.chat-scroll {
    max-height: 420px;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    gap: 16px;
    padding: 4px 2px 10px;
    margin-bottom: 12px;
}
.chat-row { display: flex; width: 100%; animation: popIn 0.35s cubic-bezier(0.16,1,0.3,1); }
@keyframes popIn {
    from { opacity:0; transform:translateY(14px) scale(0.97); }
    to   { opacity:1; transform:translateY(0) scale(1); }
}
.user-row { justify-content: flex-end; }
.bot-row  { justify-content: flex-start; }

.bubble {
    max-width: 80%;
    padding: 14px 18px;
    border-radius: 22px;
    font-size: 0.92rem;
    line-height: 1.55;
    backdrop-filter: blur(8px);
}
.user-bubble {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-bottom-right-radius: 4px;
    color: #e8e8f0;
}
.bot-bubble-wrap { display: flex; align-items: flex-start; gap: 12px; }
.avatar {
    width: 40px; height: 40px; border-radius: 50%; flex-shrink: 0;
    background: linear-gradient(135deg, #aa7c11, #d4af37);
    display: flex; align-items: center; justify-content: center;
    font-family: 'Cinzel', serif; font-size: 1.1rem; font-weight: 900;
    color: #07040a;
    box-shadow: 0 4px 15px rgba(212,175,55,0.35);
}
.bot-bubble {
    background: linear-gradient(135deg, rgba(180,50,110,0.06), rgba(212,175,55,0.03));
    border: 1px solid rgba(180,50,110,0.28);
    border-bottom-left-radius: 4px;
    color: #f0e8d0;
}
.sender-label {
    font-size: 0.66rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    margin-bottom: 5px;
    opacity: 0.75;
}
.user-bubble .sender-label { color: #a1a1aa; }
.bot-bubble .sender-label { color: #ffd54f; }

/* ─── Streamlit widget overrides ─── */
.stTextInput > div > div > input {
    background: rgba(255,255,255,0.02) !important;
    border: 1px solid rgba(180,50,110,0.3) !important;
    border-radius: 14px !important;
    color: #f3f4f6 !important;
    padding: 12px 18px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    transition: all 0.3s ease !important;
}
.stTextInput > div > div > input:focus {
    border-color: rgba(212,175,55,0.55) !important;
    box-shadow: 0 0 20px rgba(212,175,55,0.12) !important;
    background: rgba(255,255,255,0.035) !important;
}

/* Primary action button */
.stButton > button {
    background: linear-gradient(90deg, #a73a6c 0%, #c8622a 60%, #e28e57 100%) !important;
    border: none !important;
    color: #fff !important;
    border-radius: 14px !important;
    font-family: 'Cinzel', serif !important;
    font-size: 0.88rem !important;
    font-weight: 700 !important;
    letter-spacing: 1px !important;
    padding: 12px 24px !important;
    width: 100% !important;
    transition: all 0.35s cubic-bezier(0.16,1,0.3,1) !important;
    box-shadow: 0 6px 22px rgba(167,58,108,0.40) !important;
    position: relative;
    overflow: hidden;
}
.stButton > button::before {
    content: '';
    position: absolute;
    top: -50%; left: -60%;
    width: 40%; height: 200%;
    background: rgba(255,255,255,0.12);
    transform: skewX(-20deg);
    transition: left 0.5s ease;
}
.stButton > button:hover::before { left: 130%; }
.stButton > button:hover {
    transform: translateY(-3px) !important;
    box-shadow: 0 12px 35px rgba(167,58,108,0.65) !important;
    filter: brightness(1.08) !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: transparent !important;
    gap: 8px !important;
    border-bottom: 1px solid rgba(255,255,255,0.04) !important;
}
.stTabs [data-baseweb="tab"] {
    background: rgba(255,255,255,0.01) !important;
    border: 1px solid rgba(255,255,255,0.04) !important;
    border-radius: 10px 10px 0 0 !important;
    color: #888 !important;
    padding: 9px 20px !important;
    font-family: 'Cinzel', serif !important;
    font-size: 0.78rem !important;
    transition: all 0.3s ease !important;
}
.stTabs [data-baseweb="tab"]:hover { color: #ffd54f !important; border-color: rgba(180,50,110,0.3) !important; }
.stTabs [aria-selected="true"] {
    color: #fff !important;
    background: linear-gradient(135deg, rgba(180,50,110,0.55), rgba(180,50,110,0.25)) !important;
    border-color: rgba(180,50,110,0.5) !important;
    font-weight: 700 !important;
}

/* File uploader */
[data-testid="stFileUploader"] {
    border: 1.5px dashed rgba(180,50,110,0.35) !important;
    background: rgba(255,255,255,0.008) !important;
    border-radius: 18px !important;
    padding: 20px !important;
    transition: all 0.3s ease !important;
}
[data-testid="stFileUploader"]:hover {
    border-color: rgba(212,175,55,0.55) !important;
    background: rgba(212,175,55,0.02) !important;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, rgba(18,5,13,0.92) 0%, rgba(8,2,6,0.98) 100%) !important;
    border-right: 1px solid rgba(180,50,110,0.10) !important;
    box-shadow: 5px 0 40px rgba(0,0,0,0.6) !important;
}
.stSlider > label {
    color: #ffd54f !important;
    font-family: 'Cinzel', serif !important;
    font-size: 0.8rem !important;
}

/* ─── Saree Result Card ─── */
.saree-card {
    background: linear-gradient(140deg, rgba(40,8,28,0.7), rgba(15,4,11,0.9)) !important;
    border: 1px solid rgba(180,50,110,0.18) !important;
    border-radius: 22px !important;
    overflow: hidden !important;
    margin-bottom: 22px !important;
    box-shadow: 0 15px 40px rgba(0,0,0,0.5) !important;
    transition: all 0.5s cubic-bezier(0.16,1,0.3,1) !important;
    animation: cardIn 0.5s cubic-bezier(0.16,1,0.3,1);
}
@keyframes cardIn {
    from { opacity:0; transform:translateY(20px) scale(0.96); }
    to   { opacity:1; transform:translateY(0) scale(1); }
}
.saree-card:hover {
    transform: translateY(-10px) scale(1.02) !important;
    border-color: rgba(212,175,55,0.45) !important;
    box-shadow: 0 25px 55px rgba(212,175,55,0.18) !important;
}
.saree-img-wrap {
    width: 100%; height: 280px;
    overflow: hidden;
    background: #0c0409;
    border-bottom: 1px solid rgba(255,255,255,0.04);
    position: relative;
}
.saree-img {
    width:100%; height:100%;
    object-fit: cover;
    transition: transform 0.8s cubic-bezier(0.16,1,0.3,1);
}
.saree-card:hover .saree-img { transform: scale(1.1); }
.saree-overlay {
    position: absolute; bottom: 0; left: 0; right: 0; height: 60%;
    background: linear-gradient(to top, rgba(9,4,8,0.8), transparent);
    pointer-events: none;
}
.saree-info {
    padding: 18px 20px 20px;
    background: rgba(7,4,6,0.25);
}
.saree-name {
    font-family: 'Cinzel', serif;
    font-size: 0.88rem; font-weight: 600;
    color: #f4ebd0;
    line-height: 1.4;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
    height: 2.5em;
    margin: 0;
}
.saree-sku { font-size: 0.66rem; color: #7a6a7a; text-transform: uppercase; letter-spacing: 0.8px; margin: 4px 0 8px; }
.saree-tags { display:flex; flex-wrap:wrap; gap:4px; margin-bottom:10px; }
.tag {
    font-size: 0.64rem; font-weight: 600;
    padding: 2px 8px; border-radius: 6px;
    border: 1px solid; display: inline-block;
}
.saree-price { font-size: 0.88rem; margin: 6px 0; }
.price-now { color: #ffd54f; font-weight: 700; }
.price-was { color: #7a6a7a; font-size: 0.76rem; text-decoration: line-through; margin-left: 6px; }
.score-pill {
    display: inline-block;
    background: rgba(212,175,55,0.08);
    border: 1px solid rgba(212,175,55,0.35);
    color: #ffd54f;
    padding: 4px 12px; border-radius: 20px;
    font-size: 0.7rem; font-weight: 600;
    margin: 6px 0 4px;
}
.score-detail { font-size: 0.65rem; color: #7a6a7a; }
.buy-btn {
    display: inline-block; margin-top: 12px;
    background: linear-gradient(90deg, #a73a6c, #c8622a);
    color: #fff; padding: 8px 18px; border-radius: 8px;
    font-size: 0.74rem; font-weight: 700;
    text-decoration: none; letter-spacing: 0.5px;
    transition: all 0.3s ease;
    box-shadow: 0 4px 14px rgba(167,58,108,0.3);
}
.buy-btn:hover {
    box-shadow: 0 6px 20px rgba(167,58,108,0.55);
    transform: translateY(-2px);
    color:#fff;
}

/* ─── Trust Bar ─── */
.trust-bar {
    background: linear-gradient(90deg, rgba(40,8,28,0.6), rgba(20,4,14,0.8));
    border: 1px solid rgba(180,50,110,0.18);
    border-radius: 20px;
    padding: 18px 30px;
    margin-top: 30px;
    display: flex;
    justify-content: space-around;
    align-items: center;
    flex-wrap: wrap;
    gap: 18px;
    backdrop-filter: blur(12px);
}
.trust-item { display:flex; align-items:center; gap:12px; }
.trust-icon { font-size: 1.4rem; }
.trust-title { font-family:'Cinzel',serif; font-size:0.8rem; color:#f4ebd0; font-weight:700; }
.trust-desc { font-size:0.68rem; color:#7a6a7a; }

hr { border-color: rgba(180,50,110,0.15) !important; }
[data-testid="stForm"] { border:none!important; background:transparent!important; }
</style>
""", unsafe_allow_html=True)


# ─── Helpers ───────────────────────────────────────────────────
def save_uploaded_file(uploaded_file):
    os.makedirs("data", exist_ok=True)
    temp_path = "data/temp_query.jpg"
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return temp_path

def get_saree_tags(title):
    t = str(title).lower()
    mapping = [
        ("Silk","#e6b325"),("Organza","#da70d6"),("Crepe","#ff7f50"),
        ("Tissue","#40e0d0"),("Pashmina","#ff69b4"),("Banarasi","#8a2be2"),
        ("Munga","#4682b4"),("Floral","#2e8b57"),("Cotton","#a0c4ff"),
        ("Georgette","#f77f00"),
    ]
    tags = [(n,c) for n,c in mapping if n.lower() in t]
    return tags[:3] or [("Traditional","#7f8c8d")]

def img_to_b64(path):
    try:
        with open(path,"rb") as f:
            return base64.b64encode(f.read()).decode()
    except:
        return None

@st.cache_resource
def load_search_engine():
    try:
        return SareeSearchEngine()
    except Exception as e:
        st.error(f"Search engine error: {e}")
        return None

# ─── Hero Banner ───────────────────────────────────────────────
st.markdown("""<div class="hero-banner"><div class="hero-inner">
<div class="hero-brand">
<svg width="52" height="72" viewBox="0 0 52 72" fill="none" xmlns="http://www.w3.org/2000/svg" style="filter:drop-shadow(0 0 12px rgba(212,175,55,0.5))">
<line x1="10" y1="0" x2="10" y2="18" stroke="#d4af37" stroke-width="1.5"/>
<line x1="6" y1="9" x2="14" y2="9" stroke="#d4af37" stroke-width="1.5"/>
<path d="M4 18 Q10 16 16 18 L18 30 Q10 34 2 30 Z" fill="#8B1A4A" stroke="#ffd54f" stroke-width="0.8"/>
<path d="M3 30 Q10 33 17 30 L15 38 Q10 40 5 38 Z" fill="#6B1235" stroke="#d4af37" stroke-width="0.6"/>
<circle cx="10" cy="39" r="1.5" fill="#ffd54f"/>
<line x1="10" y1="41" x2="10" y2="48" stroke="#d4af37" stroke-width="1"/>
<line x1="38" y1="0" x2="38" y2="12" stroke="#d4af37" stroke-width="1.5"/>
<path d="M32 12 Q38 10 44 12 L46 22 Q38 26 30 22 Z" fill="#8B1A4A" stroke="#ffd54f" stroke-width="0.8"/>
<path d="M31 22 Q38 25 45 22 L43 30 Q38 32 33 30 Z" fill="#6B1235" stroke="#d4af37" stroke-width="0.6"/>
<circle cx="38" cy="31" r="1.5" fill="#ffd54f"/>
<line x1="38" y1="33" x2="38" y2="40" stroke="#d4af37" stroke-width="1"/>
</svg>
<div>
<div class="hero-title">TailorTalk</div>
<div class="hero-sub">Your AI Stylist for Timeless Saree Elegance</div>
</div>
</div>
<div class="hero-description">Experience the future of Indian fashion discovery. Upload a design or describe your styling preferences, and our AI agent will instantly find sarees that match your vision in our curated catalogue.</div>
<div class="feature-pills">
<div class="feature-pill"><div class="pill-icon">✨</div><div class="pill-title">AI-Powered</div><div class="pill-desc">Smart understanding of your style</div></div>
<div class="feature-pill"><div class="pill-icon">⚡</div><div class="pill-title">Instant Matches</div><div class="pill-desc">Find perfect sarees in seconds</div></div>
<div class="feature-pill"><div class="pill-icon">🎨</div><div class="pill-title">Curated Collection</div><div class="pill-desc">Premium sarees from trusted artisans</div></div>
</div>
</div></div>""", unsafe_allow_html=True)

# ─── Session State ─────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = [{"role":"assistant","content":"Namaste! I'm TailorTalk, your AI stylist. Tell me what you're looking for, and I'll find the perfect saree match!"}]
if "search_results" not in st.session_state:
    st.session_state.search_results = None
if "img_path" not in st.session_state:
    st.session_state.img_path = None

# ─── Sidebar ───────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Agent Settings")
    api_key = os.environ.get("GEMINI_API_KEY","")
    if not api_key:
        api_key = st.text_input("Gemini API Key", type="password")
    else:
        st.markdown('<div style="background:rgba(212,175,55,0.08);border:1px solid rgba(212,175,55,0.35);border-radius:10px;padding:10px;text-align:center;color:#ffd54f;font-size:0.82rem;font-weight:700;">🤖 Agent Status: Active ✨</div>', unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("### 🎚️ Similarity Weights")
    w_clip  = st.slider("Style Weight (CLIP)",  0.0, 1.0, 0.7, 0.05)
    w_color = st.slider("Color Weight",          0.0, 1.0, 0.3, 0.05)
    ws = w_clip + w_color
    wc_n = w_clip/ws if ws else 0.5
    wcolor_n = w_color/ws if ws else 0.5
    st.caption(f"Normalized — Style: {wc_n:.2f} | Color: {wcolor_n:.2f}")
    limit_matches = st.slider("Number of Matches", 1, 10, 6)
    st.markdown("---")
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = [{"role":"assistant","content":"Namaste! Chat cleared. How can I help you find your perfect saree today?"}]
        st.session_state.search_results = None
        st.session_state.img_path = None
        st.rerun()

search_engine = load_search_engine()

# ─── Layout ────────────────────────────────────────────────────
col_chat, col_gallery = st.columns([1,1], gap="large")

# ══════════════ LEFT: CHAT ══════════════
with col_chat:
    st.markdown("""<div class="panel">
<div class="panel-title">💬 Conversational Assistant</div>
<div class="panel-desc">Describe what you're looking for, or upload an image and ask for style variations.</div>
</div>""", unsafe_allow_html=True)

    st.markdown('<div class="chip-label">Try asking:</div>', unsafe_allow_html=True)
    st.markdown("""<div class="chips">
<span class="chip">Pink saree with gold border</span>
<span class="chip">Silk saree for wedding</span>
<span class="chip">Traditional Kanjeevaram</span>
<span class="chip">Cotton saree for summer</span>
</div>""", unsafe_allow_html=True)

    # Chat bubbles
    chat_html = '<div class="chat-scroll">'
    for m in st.session_state.messages:
        if m["role"] == "user":
            chat_html += f"""<div class="chat-row user-row">
<div class="bubble user-bubble">
<div class="sender-label">You</div>
{m['content']}
</div></div>"""
        else:
            chat_html += f"""<div class="chat-row bot-row">
<div class="bot-bubble-wrap">
<div class="avatar">T</div>
<div class="bubble bot-bubble">
<div class="sender-label">TailorTalk AI ✨</div>
{m['content']}
</div>
</div></div>"""
    chat_html += '</div>'
    st.markdown(chat_html, unsafe_allow_html=True)

    if not api_key:
        st.warning("Enter your Gemini API Key in the sidebar to activate the assistant.")
        st.stop()

    agent = SareeAgent(api_key=api_key, search_engine=search_engine) if search_engine else None

    if agent:
        user_input = st.chat_input("Describe your dream saree...")
        if user_input:
            st.session_state.messages.append({"role":"user","content":user_input})
            with st.spinner("Finding your perfect saree..."):
                try:
                    resp = agent.run_chat(
                        messages_history=st.session_state.messages[:-1],
                        user_message=user_input,
                        temp_image_path=st.session_state.img_path
                    )
                    if resp["tool_called"] and resp["tool_results"]:
                        st.session_state.search_results = resp["tool_results"]
                    st.session_state.messages.append({"role":"assistant","content":resp["response_text"]})
                    st.rerun()
                except Exception as e:
                    st.error(f"Agent error: {e}")

# ══════════════ RIGHT: GALLERY ══════════════
with col_gallery:
    st.markdown("""<div class="panel">
<div class="panel-title">🛍️ Visual Search Gallery</div>
<div class="panel-desc">Upload a design image or paste any image URL to discover visually similar sarees from our collection.</div>
</div>""", unsafe_allow_html=True)

    tab_upload, tab_url = st.tabs(["Upload Image", "Image URL"])
    query_image = None

    with tab_upload:
        uploaded = st.file_uploader("Upload a saree image...", type=["jpg","jpeg","png"])
        if uploaded:
            st.session_state.img_path = save_uploaded_file(uploaded)
            query_image = Image.open(uploaded)
            st.image(query_image, caption="Uploaded Query", width=180)

    with tab_url:
        url = st.text_input("Paste an image URL...")
        if url:
            try:
                r = requests.get(url, timeout=10)
                query_image = Image.open(BytesIO(r.content))
                os.makedirs("data", exist_ok=True)
                query_image.save("data/temp_query.jpg")
                st.session_state.img_path = "data/temp_query.jpg"
                st.image(query_image, caption="URL Query", width=180)
            except Exception as e:
                st.error(f"Could not load image: {e}")

    if st.button("🔍 Run Visual Search"):
        if query_image and search_engine:
            with st.spinner("Searching the catalogue..."):
                st.session_state.search_results = search_engine.search(
                    query_image=query_image, top_k=limit_matches,
                    w_clip=wc_n, w_color=wcolor_n
                )
        else:
            st.warning("Please upload an image or provide a URL first.")

    st.markdown("---")

    if st.session_state.search_results:
        st.markdown(f"#### ✨ Top {len(st.session_state.search_results)} Matches")
        cols = st.columns(2)
        for idx, item in enumerate(st.session_state.search_results):
            with cols[idx % 2]:
                b64 = img_to_b64(item["relative_path"])
                img_tag = f'<img src="data:image/webp;base64,{b64}" class="saree-img"/>' if b64 else ""

                tags = get_saree_tags(item.get("name",""))
                tags_html = "".join(
                    f'<span class="tag" style="background:{c}18;border-color:{c}50;color:{c}">{n}</span>'
                    for n,c in tags
                )

                price_html = ""
                if item.get("discounted_price") and item.get("retail_price"):
                    price_html = f'<div class="saree-price"><span class="price-now">₹{item["discounted_price"]}</span><span class="price-was">₹{item["retail_price"]}</span></div>'
                elif item.get("discounted_price"):
                    price_html = f'<div class="saree-price"><span class="price-now">₹{item["discounted_price"]}</span></div>'

                buy_html = ""
                if item.get("website_link"):
                    buy_html = f'<a href="{item["website_link"]}" target="_blank" class="buy-btn">Buy Now ↗</a>'

                st.markdown(f"""<div class="saree-card">
<div class="saree-img-wrap">{img_tag}<div class="saree-overlay"></div></div>
<div class="saree-info">
<div class="saree-name">{item.get('name', item['filename'])}</div>
<div class="saree-sku">SKU: {item.get('sku', item['filename'])}</div>
<div class="saree-tags">{tags_html}</div>
{price_html}
<div><span class="score-pill">Match: {item['score']*100:.1f}%</span></div>
<div class="score-detail">Style: {item['clip_score']*100:.1f}% | Color: {item['color_score']*100:.1f}%</div>
{buy_html}
</div></div>""", unsafe_allow_html=True)
    else:
        st.markdown("""<div style="background:rgba(180,50,110,0.05);border:1px solid rgba(180,50,110,0.15);border-radius:16px;padding:30px;text-align:center;color:#7a6a7a;">
<div style="font-size:2rem;margin-bottom:10px;">🧵</div>
<div style="font-family:'Cinzel',serif;font-size:0.88rem;color:#c4b5c4;">Upload an image or chat with the assistant to discover sarees</div>
</div>""", unsafe_allow_html=True)

# ─── Trust Footer ──────────────────────────────────────────────
st.markdown("""<div class="trust-bar">
<div class="trust-item"><span class="trust-icon">🏺</span><div><div class="trust-title">1000+ Premium Sarees</div><div class="trust-desc">Curated pure silk &amp; organza catalog</div></div></div>
<div class="trust-item"><span class="trust-icon">🧑‍🎨</span><div><div class="trust-title">Trusted Artisans</div><div class="trust-desc">Authentic handloom craftsmanship</div></div></div>
<div class="trust-item"><span class="trust-icon">🛡️</span><div><div class="trust-title">Secure &amp; Private</div><div class="trust-desc">Your style data is protected</div></div></div>
<div class="trust-item"><span class="trust-icon">🤖</span><div><div class="trust-title">24/7 AI Assistant</div><div class="trust-desc">Always here to help you style</div></div></div>
</div>""", unsafe_allow_html=True)
