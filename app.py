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

# ── Load CSS from file (only reliable cross-platform method) ──────────────────
def load_css(path):
    with open(path, "r", encoding="utf-8") as f:
        css = f.read()
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

load_css("style.css")

# ─── Helpers ──────────────────────────────────────────────────────────────────
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
        with open(path, "rb") as f:
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

# ─── Hero Banner ──────────────────────────────────────────────────────────────
st.markdown("""<div class="hero-banner"><div class="hero-inner"><div class="hero-brand"><svg width="52" height="72" viewBox="0 0 52 72" fill="none" xmlns="http://www.w3.org/2000/svg" style="filter:drop-shadow(0 0 12px rgba(212,175,55,0.5))"><line x1="10" y1="0" x2="10" y2="18" stroke="#d4af37" stroke-width="1.5"/><line x1="6" y1="9" x2="14" y2="9" stroke="#d4af37" stroke-width="1.5"/><path d="M4 18 Q10 16 16 18 L18 30 Q10 34 2 30 Z" fill="#8B1A4A" stroke="#ffd54f" stroke-width="0.8"/><path d="M3 30 Q10 33 17 30 L15 38 Q10 40 5 38 Z" fill="#6B1235" stroke="#d4af37" stroke-width="0.6"/><circle cx="10" cy="39" r="1.5" fill="#ffd54f"/><line x1="10" y1="41" x2="10" y2="48" stroke="#d4af37" stroke-width="1"/><line x1="38" y1="0" x2="38" y2="12" stroke="#d4af37" stroke-width="1.5"/><path d="M32 12 Q38 10 44 12 L46 22 Q38 26 30 22 Z" fill="#8B1A4A" stroke="#ffd54f" stroke-width="0.8"/><path d="M31 22 Q38 25 45 22 L43 30 Q38 32 33 30 Z" fill="#6B1235" stroke="#d4af37" stroke-width="0.6"/><circle cx="38" cy="31" r="1.5" fill="#ffd54f"/><line x1="38" y1="33" x2="38" y2="40" stroke="#d4af37" stroke-width="1"/></svg><div><div class="hero-title">TailorTalk</div><div class="hero-sub">Your AI Stylist for Timeless Saree Elegance</div></div></div><div class="hero-description">Experience the future of Indian fashion discovery. Upload a design or describe your styling preferences, and our AI agent will instantly find sarees that match your vision in our curated catalogue.</div><div class="feature-pills"><div class="feature-pill"><div class="pill-icon">✨</div><div class="pill-title">AI-Powered</div><div class="pill-desc">Smart understanding of your style</div></div><div class="feature-pill"><div class="pill-icon">⚡</div><div class="pill-title">Instant Matches</div><div class="pill-desc">Find perfect sarees in seconds</div></div><div class="feature-pill"><div class="pill-icon">🎨</div><div class="pill-title">Curated Collection</div><div class="pill-desc">Premium sarees from trusted artisans</div></div></div></div></div>""", unsafe_allow_html=True)

# ─── Session State ─────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Namaste! I'm TailorTalk, your AI stylist. Tell me what you're looking for, and I'll find the perfect saree match!"}]
if "search_results" not in st.session_state:
    st.session_state.search_results = None
if "img_path" not in st.session_state:
    st.session_state.img_path = None

# ─── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Agent Settings")
    # Check Streamlit Cloud secrets first, then env var, then manual input
    api_key = ""
    try:
        api_key = st.secrets.get("GEMINI_API_KEY", "")
    except Exception:
        pass
    if not api_key:
        api_key = os.environ.get("GEMINI_API_KEY", "")
    if api_key:
        st.markdown('<div style="background:rgba(212,175,55,0.08);border:1px solid rgba(212,175,55,0.35);border-radius:10px;padding:10px;text-align:center;color:#ffd54f;font-size:0.82rem;font-weight:700;">🤖 Agent Status: Active ✨</div>', unsafe_allow_html=True)
    else:
        api_key = st.text_input("Gemini API Key", type="password")
    st.markdown("---")
    st.markdown("### 🎚️ Similarity Weights")
    w_clip  = st.slider("Style Weight (CLIP)",  0.0, 1.0, 0.7, 0.05)
    w_color = st.slider("Color Weight",          0.0, 1.0, 0.3, 0.05)
    ws = w_clip + w_color
    wc_n     = w_clip  / ws if ws else 0.5
    wcolor_n = w_color / ws if ws else 0.5
    st.caption(f"Normalized — Style: {wc_n:.2f} | Color: {wcolor_n:.2f}")
    limit_matches = st.slider("Number of Matches", 1, 10, 6)
    st.markdown("---")
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = [{"role": "assistant", "content": "Namaste! Chat cleared. How can I help you find your perfect saree today?"}]
        st.session_state.search_results = None
        st.session_state.img_path = None
        st.rerun()

search_engine = load_search_engine()

# ─── Layout ───────────────────────────────────────────────────────────────────
col_chat, col_gallery = st.columns([1, 1], gap="large")

# ══════════════ LEFT: CHAT ══════════════
with col_chat:
    st.markdown('<div class="panel"><div class="panel-title">💬 Conversational Assistant</div><div class="panel-desc">Describe what you\'re looking for, or upload an image and ask for style variations.</div></div>', unsafe_allow_html=True)
    st.markdown('<div class="chip-label">Try asking:</div>', unsafe_allow_html=True)
    st.markdown('<div class="chips"><span class="chip">Pink saree with gold border</span><span class="chip">Silk saree for wedding</span><span class="chip">Traditional Kanjeevaram</span><span class="chip">Cotton saree for summer</span></div>', unsafe_allow_html=True)

    # Render chat history
    rows = []
    for m in st.session_state.messages:
        if m["role"] == "user":
            rows.append(f'<div class="chat-row user-row"><div class="bubble user-bubble"><div class="sender-label">You</div>{m["content"]}</div></div>')
        else:
            rows.append(f'<div class="chat-row bot-row"><div class="bot-bubble-wrap"><div class="avatar">T</div><div class="bubble bot-bubble"><div class="sender-label">TailorTalk AI ✨</div>{m["content"]}</div></div></div>')
    st.markdown(f'<div class="chat-scroll">{"".join(rows)}</div>', unsafe_allow_html=True)

    if not api_key:
        st.warning("Enter your Gemini API Key in the sidebar to activate the assistant.")
        st.stop()

    agent = SareeAgent(api_key=api_key, search_engine=search_engine) if search_engine else None

    if agent:
        user_input = st.chat_input("Describe your dream saree...")
        if user_input:
            st.session_state.messages.append({"role": "user", "content": user_input})
            with st.spinner("Finding your perfect saree..."):
                try:
                    resp = agent.run_chat(
                        messages_history=st.session_state.messages[:-1],
                        user_message=user_input,
                        temp_image_path=st.session_state.img_path
                    )
                    if resp["tool_called"] and resp["tool_results"]:
                        st.session_state.search_results = resp["tool_results"]
                    st.session_state.messages.append({"role": "assistant", "content": resp["response_text"]})
                    st.rerun()
                except Exception as e:
                    st.error(f"Agent error: {e}")

# ══════════════ RIGHT: GALLERY ══════════════
with col_gallery:
    st.markdown('<div class="panel"><div class="panel-title">🛍️ Visual Search Gallery</div><div class="panel-desc">Upload a design image or paste any image URL to discover similar sarees from our collection.</div></div>', unsafe_allow_html=True)

    tab_upload, tab_url = st.tabs(["Upload Image", "Image URL"])
    query_image = None

    with tab_upload:
        uploaded = st.file_uploader("Upload a saree image...", type=["jpg", "jpeg", "png"])
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

                tags = get_saree_tags(item.get("name", ""))
                tags_html = "".join(
                    f'<span class="tag" style="background:{c}18;border-color:{c}50;color:{c}">{n}</span>'
                    for n, c in tags
                )

                price_html = ""
                if item.get("discounted_price") and item.get("retail_price"):
                    price_html = f'<div class="saree-price"><span class="price-now">&#8377;{item["discounted_price"]}</span><span class="price-was">&#8377;{item["retail_price"]}</span></div>'
                elif item.get("discounted_price"):
                    price_html = f'<div class="saree-price"><span class="price-now">&#8377;{item["discounted_price"]}</span></div>'

                buy_html = ""
                if item.get("website_link"):
                    buy_html = f'<a href="{item["website_link"]}" target="_blank" class="buy-btn">Buy Now &#8599;</a>'

                st.markdown(f"""<div class="saree-card"><div class="saree-img-wrap">{img_tag}<div class="saree-overlay"></div></div><div class="saree-info"><div class="saree-name">{item.get('name', item['filename'])}</div><div class="saree-sku">SKU: {item.get('sku', item['filename'])}</div><div class="saree-tags">{tags_html}</div>{price_html}<div><span class="score-pill">Match: {item['score']*100:.1f}%</span></div><div class="score-detail">Style: {item['clip_score']*100:.1f}% | Color: {item['color_score']*100:.1f}%</div>{buy_html}</div></div>""", unsafe_allow_html=True)
    else:
        st.markdown('<div style="background:rgba(180,50,110,0.05);border:1px solid rgba(180,50,110,0.15);border-radius:16px;padding:30px;text-align:center;"><div style="font-size:2rem;margin-bottom:10px;">🧵</div><div style="font-family:Cinzel,serif;font-size:0.88rem;color:#c4b5c4;">Upload an image or chat with the assistant to discover sarees</div></div>', unsafe_allow_html=True)

# ─── Trust Footer ─────────────────────────────────────────────────────────────
st.markdown('<div class="trust-bar"><div class="trust-item"><span class="trust-icon">🏺</span><div><div class="trust-title">1000+ Premium Sarees</div><div class="trust-desc">Curated pure silk &amp; organza catalog</div></div></div><div class="trust-item"><span class="trust-icon">🧑&#8203;&#127912;</span><div><div class="trust-title">Trusted Artisans</div><div class="trust-desc">Authentic handloom craftsmanship</div></div></div><div class="trust-item"><span class="trust-icon">🛡️</span><div><div class="trust-title">Secure &amp; Private</div><div class="trust-desc">Your style data is protected</div></div></div><div class="trust-item"><span class="trust-icon">🤖</span><div><div class="trust-title">24/7 AI Assistant</div><div class="trust-desc">Always here to help you style</div></div></div></div>', unsafe_allow_html=True)
