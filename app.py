import streamlit as st
import os

# 1. Page Config & CSS
st.set_page_config(page_title="FlexFly", page_icon="✈️", layout="centered")

# Custom CSS to fix the input alignment and ghost borders
st.markdown("""
    <style>
    /* 1. Eliminate the ghost border/margin on the input container */
    div[data-baseweb="input"] {
        border: none !important;
        background-color: transparent !important;
    }

    /* 2. Style the actual input field to match your rounded container */
    .stTextInput input {
        color: #000000;
        background-color: #ffffff !important;
        border-radius: 30px !important; /* Matches the parent container rounding */
        padding: 12px 20px !important;
        border: none !important;
    }

    /* 3. Hide the ugly blue 'focus' border Streamlit adds */
    .stTextInput div[data-baseweb="input"]:focus-within {
        box-shadow: none !important;
        border: none !important;
    }

    /* 4. Style markdown tables with rounded borders and modern UI */
    .stMarkdown table {
        border-collapse: separate !important;
        border-spacing: 0 !important;
        width: 100% !important;
        border-radius: 12px !important;
        overflow: hidden !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1) !important;
        background-color: #ffffff !important;
        margin: 20px 0 !important;
    }

    .stMarkdown thead {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: #ffffff !important;
    }

    .stMarkdown thead th {
        padding: 16px 20px !important;
        text-align: left !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
        border: none !important;
    }

    .stMarkdown tbody tr {
        transition: background-color 0.2s ease !important;
        border-bottom: 1px solid #f0f0f0 !important;
    }

    .stMarkdown tbody tr:hover {
        background-color: #f8f9fa !important;
    }

    .stMarkdown tbody tr:last-child {
        border-bottom: none !important;
    }

    .stMarkdown tbody td {
        padding: 14px 20px !important;
        border: none !important;
        color: #333333 !important;
        font-size: 14px !important;
    }

    .stMarkdown tbody tr:nth-child(even) {
        background-color: #fafafa !important;
    }

    .stMarkdown tbody tr:nth-child(even):hover {
        background-color: #f0f0f0 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Load OpenAI Key Standard
if "OPENAI_API_KEY" in st.secrets:
    os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]

# 3. UI Layout
st.markdown('<h1 class="main-title">FlexFly</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Agentic Search for the Unlimited Leave Traveler</p>', unsafe_allow_html=True)

col1, col2 = st.columns([0.9, 0.1])
with col1:
    query = st.text_input("", label_visibility="collapsed")
with col2:
    st.button("🔍")

if query:
    if "OPENAI_API_KEY" not in os.environ:
        st.error("⚠️ API Key missing. Please check .streamlit/secrets.toml")
        st.stop()
    
    with st.spinner("⏳ Agents are scanning the forums..."):
        try:
            from src.agents import run_flight
            result = run_flight(query)
            
            st.divider()
            st.markdown(result)
            st.success("Scan Complete.")
            
        except Exception as e:
            st.error(f"Error: {e}")