import streamlit as st
import os

# 1. Page Config & CSS
st.set_page_config(page_title="FlexFly Sniper", page_icon="✈️", layout="centered")

st.markdown("""
    <style>
    .stTextInput > label {display: none;}
    .stTextInput input {
        font-size: 22px;
        padding: 15px 20px;
        border-radius: 30px;
        border: 1px solid #5f6368;
        background-color: #f1f3f4;
        color: #000;
    }
    .stTextInput input:focus {
        border-color: #8ab4f8;
        box-shadow: 0 1px 6px rgba(138, 180, 248, 0.2);
    }
    .main-title {
        text-align: center;
        font-family: 'Helvetica Neue', sans-serif;
        font-weight: 200;
        font-size: 3.5rem;
        margin-top: 60px;
        margin-bottom: 0px;
        color: #202124;
    }
    .subtitle {
        text-align: center;
        color: #5f6368;
        font-size: 1.2rem;
        margin-bottom: 40px;
    }
    </style>
""", unsafe_allow_html=True)

# 2. Load OpenAI Key Standard
if "OPENAI_API_KEY" in st.secrets:
    os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]

# 3. UI Layout
st.markdown('<h1 class="main-title">FlexFly Sniper</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Agentic Search for the Unlimited Leave Traveler</p>', unsafe_allow_html=True)

query = st.text_input("Search", placeholder="e.g. Business class glitch to Japan 2026")

if query:
    if "OPENAI_API_KEY" not in os.environ:
        st.error("⚠️ API Key missing. Please check .streamlit/secrets.toml")
        st.stop()
    
    with st.spinner("🕵️ Agents are scanning the forums..."):
        try:
            from src.agents import run_flight_sniper
            result = run_flight_sniper(query)
            
            st.divider()
            st.markdown(result)
            st.success("Scan Complete.")
            
        except Exception as e:
            st.error(f"Error: {e}")