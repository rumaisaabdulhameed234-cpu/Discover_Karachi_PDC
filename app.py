import streamlit as st
import random
from groq import Groq
import os
import html
import re
from rag_utils import search_places  # 🔍 Importing your RAG search utility

st.set_page_config(
    page_title="Discover Karachi",
    page_icon=None,
    layout="centered"
)

# Load CSS from external file
def load_css(file_name):
    if os.path.exists(file_name):
        with open(file_name) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    else:
        st.warning("style.css not found — running without styling")

load_css("style.css")

# Floating background decorations
st.markdown("""
    <div class="bg-decorations">
        <span style="top:5%; left:3%; animation-delay:0s;">🍓</span>
        <span style="top:12%; left:90%; animation-delay:1s;">💚</span>
        <span style="top:25%; left:8%; animation-delay:2s;">💚</span>
        <span style="top:20%; left:75%; animation-delay:0.5s;">🍓</span>
        <span style="top:40%; left:95%; animation-delay:1.5s;">🍓</span>
        <span style="top:50%; left:2%; animation-delay:3s;">💚</span>
        <span style="top:60%; left:85%; animation-delay:2.5s;">💚</span>
        <span style="top:70%; left:10%; animation-delay:1s;">🍓</span>
        <span style="top:80%; left:92%; animation-delay:0.5s;">🍓</span>
        <span style="top:88%; left:20%; animation-delay:2s;">💚</span>
        <span style="top:35%; left:50%; animation-delay:3.5s;">🍓</span>
        <span style="top:55%; left:60%; animation-delay:1.8s;">💚</span>
    </div>
""", unsafe_allow_html=True)

# Header
st.markdown("""
    <div class="main-header">
        <div class="main-title">Discover Karachi</div>
        <div class="main-subtitle">your personal guide to cafes, restaurants & places in Karachi</div>
    </div>
""", unsafe_allow_html=True)

# Groq client
groq_api_key = st.secrets["GROQ_API_KEY"]

# System prompt (Enforces utilizing the RAG context details safely)
system_prompt = """
You are Discover Karachi, a warm and friendly chatbot that answers questions 
about restaurants, cafes, food spots, and places to visit in Karachi, Pakistan.

IMPORTANT RULES:
- Only recommend places from the provided context database.
- Do NOT make up places or list facts outside what is verified in the retrieved documents.
- Always mention the area, price range, and vibe.
- Keep your tone warm, welcoming, and conversational.

If asked anything NOT about Karachi food or places, say:
"I only know about food and places in Karachi! Ask me about cafes, restaurants or spots to visit."

FORMATTING RULES (very important):
- Respond in plain, natural text only.
- NEVER include HTML tags (like <div>, <span>, <br>) in your response.
- NEVER include markdown syntax like **bold**, ##, or backticks.
- Just write normal sentences, like you're chatting with a friend.
"""

def clean_reply(text: str) -> str:
    """Safety net: strip any stray HTML tags the model might emit."""
    text = re.sub(r"<[^>]+>", "", text)
    text = html.unescape(text)
    return text.strip()

# Session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history (Preserves your custom user bubbles and polaroids!)
for message in st.session_state.messages:
    if message["role"] == "user":
        st.markdown(f"""
            <div class="user-bubble">
                <div class="user-bubble-inner">{html.escape(message["content"])}</div>
            </div>
        """, unsafe_allow_html=True)
    else:
        tilt = "tilt-left" if random.random() > 0.5 else "tilt-right"
        st.markdown(f"""
            <div class="bot-polaroid">
                <div class="polaroid-card {tilt}">
                    {html.escape(message["content"])}
                    <div class="polaroid-label">— discover karachi</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

# Chat input
if prompt := st.chat_input("ask me about cafes and places in karachi..."):

    st.markdown(f"""
        <div class="user-bubble">
            <div class="user-bubble-inner">{html.escape(prompt)}</div>
        </div>
    """, unsafe_allow_html=True)

    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.spinner("finding the best spots for you..."):

        # 🔍 Step 1: Run RAG retrieval script using the user query
        results = search_places(prompt)

        # Step 2: Format the retrieved location context beautifully
        context = "\n".join([
            f"{r['name']} ({r['area']}): {r['description']} | Price: {r['price']} | Vibe: {r['vibe']}"
            for r in results
        ])

        # Step 3: Inject the custom database snapshot directly into the conversation instructions
        rag_prompt = f"""
User query: {prompt}

Relevant Karachi places from database:
{context}

Answer using ONLY the database places listed above. Respond in plain text with no HTML or markdown.
"""

        # Step 4: Call Groq API model supplying context data along with history logs
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "system", "content": rag_prompt}
            ] + st.session_state.messages[:-1],  # pass history excluding the duplicate prompt we attached
            max_tokens=500
        )
        bot_reply = clean_reply(response.choices[0].message.content)

    # Step 5: Render inside your stylized Polaroid view block element
    tilt = "tilt-left" if random.random() > 0.5 else "tilt-right"
    st.markdown(f"""
        <div class="bot-polaroid">
            <div class="polaroid-card {tilt}">
                {html.escape(bot_reply)}
                <div class="polaroid-label">— discover karachi</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.session_state.messages.append({"role": "assistant", "content": bot_reply})