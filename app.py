import os
import streamlit as st
import textwrap
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

# Inject custom CSS for premium fashion aesthetics (Glassmorphism & Luxury Typography)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@600;800&family=Inter:wght@300;400;500;600&display=swap');

    /* Hide Streamlit default headers/footers for app customization */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Main Layout */
    .stApp {
        background-color: #0d0e12;
        color: #f3f4f6;
        font-family: 'Inter', sans-serif;
    }
    
    /* Header and Titles */
    h1, h2, h3, .title-text {
        font-family: 'Cinzel', serif !important;
        background: linear-gradient(135deg, #f5d061, #e6b325, #aa7c11);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        letter-spacing: 0.5px;
    }
    
    /* Custom Chat Container */
    .chat-container {
        max-height: 520px;
        overflow-y: auto;
        padding: 15px;
        display: flex;
        flex-direction: column;
        gap: 16px;
        border-radius: 16px;
        background: rgba(255, 255, 255, 0.01);
        border: 1px solid rgba(255, 255, 255, 0.05);
        margin-bottom: 20px;
    }
    .chat-container::-webkit-scrollbar {
        width: 6px;
    }
    .chat-container::-webkit-scrollbar-track {
        background: transparent;
    }
    .chat-container::-webkit-scrollbar-thumb {
        background: rgba(230, 179, 37, 0.25);
        border-radius: 10px;
    }
    .chat-container::-webkit-scrollbar-thumb:hover {
        background: rgba(230, 179, 37, 0.45);
    }
    
    .chat-row {
        display: flex;
        width: 100%;
    }
    .user-row {
        justify-content: flex-end;
    }
    .assistant-row {
        justify-content: flex-start;
    }
    .chat-bubble {
        max-width: 80%;
        padding: 14px 18px;
        border-radius: 20px;
        font-size: 0.92rem;
        line-height: 1.45;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
    }
    .user-bubble {
        background: rgba(255, 255, 255, 0.04);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-bottom-right-radius: 4px;
        color: #f3f4f6;
    }
    .assistant-bubble {
        background: rgba(230, 179, 37, 0.04);
        border: 1px solid rgba(230, 179, 37, 0.22);
        border-bottom-left-radius: 4px;
        color: #f5d061;
    }
    .bubble-sender {
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        margin-bottom: 6px;
        letter-spacing: 0.8px;
        opacity: 0.85;
    }
    .user-bubble .bubble-sender {
        color: #a1a1aa;
    }
    .assistant-bubble .bubble-sender {
        color: #e6b325;
    }
    
    /* Glassmorphism Saree Card */
    .saree-card {
        background: rgba(255, 255, 255, 0.02) !important;
        backdrop-filter: blur(12px) saturate(180%) !important;
        -webkit-backdrop-filter: blur(12px) saturate(180%) !important;
        border: 1px solid rgba(255, 255, 255, 0.06) !important;
        border-radius: 20px !important;
        padding: 16px !important;
        text-align: center !important;
        transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1) !important;
        margin-bottom: 24px !important;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3) !important;
    }
    .saree-card:hover {
        transform: translateY(-10px) scale(1.015) !important;
        border-color: rgba(230, 179, 37, 0.45) !important;
        box-shadow: 0 16px 40px rgba(230, 179, 37, 0.18) !important;
        background: rgba(255, 255, 255, 0.04) !important;
    }
    
    /* Similarity Score Badge (Glassmorphic Gold) */
    .score-badge {
        background: rgba(230, 179, 37, 0.08) !important;
        backdrop-filter: blur(4px) !important;
        border: 1px solid rgba(230, 179, 37, 0.35) !important;
        color: #f5d061 !important;
        padding: 6px 14px !important;
        border-radius: 30px !important;
        font-weight: 600 !important;
        font-size: 0.76rem !important;
        display: inline-block !important;
        margin-top: 8px !important;
        box-shadow: 0 2px 10px rgba(230, 179, 37, 0.05) !important;
    }
    
    /* Breakdown Scores */
    .breakdown-text {
        font-size: 0.72rem !important;
        color: #9ca3af !important;
        margin-top: 6px !important;
        letter-spacing: 0.2px !important;
    }
    
    /* Premium Buy Button */
    .buy-button {
        display: inline-block !important;
        margin-top: 14px !important;
        background: linear-gradient(135deg, #aa7c11, #e6b325) !important;
        color: #0d0e12 !important;
        padding: 8px 20px !important;
        border-radius: 8px !important;
        font-size: 0.78rem !important;
        font-weight: 700 !important;
        text-decoration: none !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(230, 179, 37, 0.2) !important;
        border: none !important;
    }
    .buy-button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 22px rgba(230, 179, 37, 0.5) !important;
        color: #000000 !important;
    }
    
    /* Streamlit Form Input styling */
    .stTextInput > div > div > input {
        background-color: rgba(255, 255, 255, 0.02) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 8px !important;
        color: #f3f4f6 !important;
        backdrop-filter: blur(5px) !important;
    }
    .stTextInput > div > div > input:focus {
        border-color: rgba(230, 179, 37, 0.6) !important;
        box-shadow: 0 0 10px rgba(230, 179, 37, 0.2) !important;
    }
    
    /* Sidebar glassmorphism */
    section[data-testid="stSidebar"] {
        background: rgba(13, 14, 18, 0.8) !important;
        backdrop-filter: blur(20px) !important;
        -webkit-backdrop-filter: blur(20px) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.04) !important;
    }
    
    /* Divider styling */
    hr {
        border-color: rgba(230, 179, 37, 0.15) !important;
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
    # Fabric
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
    # Weave/Type
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
st.markdown("""<div style="background: rgba(255, 255, 255, 0.02); border: 1px solid rgba(255, 255, 255, 0.05); padding: 24px; border-radius: 16px; margin-bottom: 24px; backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px); box-shadow: 0 4px 30px rgba(0, 0, 0, 0.2);">
<h1 style="margin: 0; font-size: 2.2rem; font-family: 'Cinzel', serif; background: linear-gradient(135deg, #f5d061, #e6b325, #aa7c11); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">🏮 TailorTalk</h1>
<p style="margin: 6px 0 0 0; color: #9ca3af; font-size: 0.95rem; font-family: 'Inter', sans-serif; letter-spacing: 0.1px;">Experience the future of Indian fashion discovery. Upload a design or describe your styling preferences, and our conversational AI agent will query a fine-grained vector catalogue of sarees to find visual and semantic matches instantly.</p>
</div>""", unsafe_allow_html=True)

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
if st.sidebar.button("Clear Chat History"):
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

# Right Column: Visual Similarity Search Results
with col_results:
    st.subheader("🛍️ Visual Search Gallery")
    
    # Image Input section (Upload or link)
    st.markdown("### Image Input Query")
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
                # Save to temp path
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
                # Load saree image
                img_path = item["relative_path"]
                if os.path.exists(img_path):
                    saree_img = Image.open(img_path)
                else:
                    saree_img = None
                    
                # Format price details
                price_html = ""
                if item.get("discounted_price") and item.get("retail_price"):
                    price_html = f"""<p style="margin: 5px 0 0 0; font-size: 0.9rem;">
<span style="color: #d4af37; font-weight: bold;">₹{item['discounted_price']}</span>
<span style="text-decoration: line-through; color: #888; font-size: 0.8rem; margin-left: 5px;">₹{item['retail_price']}</span>
</p>"""
                elif item.get("discounted_price"):
                    price_html = f'<p style="margin: 5px 0 0 0; font-size: 0.9rem; color: #d4af37; font-weight: bold;">₹{item["discounted_price"]}</p>'
                
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
<p style="font-weight: 600; margin: 0; color: #f3e5ab; font-size: 0.9rem; line-height: 1.2; height: 2.4em; overflow: hidden; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical;">{item.get('name', item['filename'])}</p>
<p style="margin: 2px 0 0 0; font-size: 0.75rem; color: #888;">SKU: {item.get('sku', item['filename'])}</p>
{tags_html}
{price_html}
<div class="score-badge" style="margin-top: 8px;">Match: {item['score']*100:.1f}%</div>
<div class="breakdown-text">Style: {item['clip_score']*100:.1f}% | Color: {item['color_score']*100:.1f}%</div>
{buy_button_html}
</div>"""
                st.markdown(card_html, unsafe_allow_html=True)
                if saree_img:
                    st.image(saree_img, width="stretch")
    else:
        st.info("No active search results. Perform a Visual Search or chat with the agent to populate this gallery.")

# Left Column: Chat Assistant
with col_chat:
    st.subheader("💬 Chat with TailorTalk Assistant")
    
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
        user_input = st.chat_input("Ask TailorTalk (e.g. 'What is saree QS204820 like?' or 'Find blue organza sarees')")
        
        if user_input:
            # 1. Display user message
            st.session_state.messages.append({"role": "user", "content": user_input})
            
            # 2. Run agent response
            with st.spinner("TailorTalk is thinking..."):
                try:
                    img_path_query = st.session_state.current_image_path if st.session_state.current_image_path else None
                    
                    response = agent.run_chat(
                        messages_history=st.session_state.messages[:-1], # History before the new message
                        user_message=user_input,
                        temp_image_path=img_path_query
                    )
                    
                    # If the agent called the visual search tool behind the scenes, update UI results
                    if response["tool_called"] and response["tool_results"]:
                        st.session_state.search_results = response["tool_results"]
                        
                    # Save assistant response
                    st.session_state.messages.append({"role": "assistant", "content": response["response_text"]})
                    
                    # Rerun to refresh the visual results panel in the right column
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"Agent error: {e}")
