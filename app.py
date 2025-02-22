"""
Quadropic OSS
https://oss.quadropic.com
Author: [Mohamed Kamran , ]
Date: Feb 21st 2025

This file contains the implementation of the Firecrawl search functionality.
"""


import streamlit as st
import time
import os
from typing import Dict, Any
from dotenv import load_dotenv, set_key
from dataclasses import dataclass
from relearnweb_backend import graph, ResearchAgentState
from typing import Dict, Any
from utils.accessibility import get_voice_input, speak_text



# Constants
ENV_KEYS = {
    "LLM_ENDPOINT": "",
    "LLM_API_KEY": "",
    "LLM_MODEL_ID": "",
    "FIRECRAWL_API_KEY": ""
}


# Set Title and Description
st.set_page_config(
    page_title="RelearnWeb",
    page_icon="🧠",
    layout="centered",
    menu_items={
        "About": """This is a research and learning tool for the web.
        A Joint Effort by Quadropic OSS and Open Source Contributers.""",
        "Get Help": "mailto:oss@quadropic.com",
    }
)

# Added custom CSS for enhanced UI aesthetics
st.markdown("""
    <style>
    body {
        background: url('https://as1.ftcdn.net/v2/jpg/05/32/80/86/1000_F_532808677_TWEq8CNGqcHmEGDOsda6o5Wi0jiDVj1p.jpg') no-repeat center center fixed;
        background-size: cover;
        color: #ffffff;
    }
    .stApp {
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.5);
        border-radius: 15px;
        padding: 20px;
        border: 1px solid #2c3e50;
        background-color: rgba(0, 0, 0, 0.7); /* Semi-transparent black background */
    }
    .stSidebar {
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.5);
        border-radius: 15px;
        padding: 20px;
        border: 1px solid #2c3e50;
        background-color: rgba(0, 0, 0, 0.7); /* Semi-transparent black background */
    }
    .stButton button {
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.5);
        border-radius: 5px;
        border: 1px solid #2c3e50;
        background-color: #2c3e50; /* New button background color */
        color: #ffffff; /* Button text color */
    }
    .stHeader {
        text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5);
    }
    </style>
""", unsafe_allow_html=True)

@dataclass
class AppState:
    research_in_progress: bool = False
    show_settings: bool = False

def init_session_state():
    """Initialize session state variables"""
    if 'state' not in st.session_state:
        st.session_state.state = AppState()

def load_settings() -> Dict[str, str]:
    """Load settings from .env file"""
    load_dotenv()
    return {key: os.getenv(key, default) for key, default in ENV_KEYS.items()}

def save_settings(settings: Dict[str, str]):
    """Save settings to .env file"""
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    for key, value in settings.items():
        set_key(env_path, key, value)

def render_header():
    """Render application header"""
    st.title("RelearnWeb")
    st.write("Research and Learn the Web like a Pro. An FOSS Alternative to OpenAI's DeepResearch.")
    st.write("A Joint Effort by Quadropic OSS and Open Source Contributers")
    st.markdown("[Learn more about Quadropic](https://quadropic.com)")

def render_sidebar() -> Dict[str, Any]:
    """Render sidebar and return research parameters"""
    st.sidebar.header("Research Parameters")
    
    # --- Accessibility Tools Section ---
    st.sidebar.subheader("Accessibility Tools")
    
    # Voice Search: Capture voice input and store it in session state
    if st.sidebar.button("🎤 Voice Search"):
        voice_query = get_voice_input("Please say your research query")
        st.session_state.voice_query = voice_query
        st.sidebar.success(f"Voice query recognized: {voice_query}")
    
    # Speak Aloud: Read out the recognized voice query (or a default message)
    if st.sidebar.button("🔊 Speak Aloud"):
        current_query = st.session_state.get("voice_query", "No voice query recognized yet")
        speak_text(current_query)
    
    # --- Normal Text Input Section ---
    query = st.sidebar.text_input("Research Query", "Quantum Computing breakthroughs")
    st.session_state.query = query
    
    depth = st.sidebar.number_input("Depth", value=1, min_value=0, max_value=10)
    breadth = st.sidebar.number_input("Breadth", value=3, min_value=1, max_value=10)
    
    params = {
        "query": query,
        "depth": depth,
        "breadth": breadth
    }
    return params


def render_settings():
    """Render settings form"""
    with st.form("settings_form"):
        st.subheader("AI Settings Configuration")
        current_settings = load_settings()
        new_settings = {
            key: st.text_input(
                key.replace("_", " ").title(), 
                value=current_settings[key],
                type="password" if "API_KEY" in key else "default"
            ) for key in ENV_KEYS
        }
        
        if st.form_submit_button("Save Settings"):
            save_settings(new_settings)
            st.success("Settings saved successfully!")
            st.session_state.state.show_settings = False
            st.rerun()
        
        if st.form_submit_button("Cancel"):
            st.session_state.state.show_settings = False
            st.rerun()

def run_research(params: Dict[str, Any]):
    """Execute research pipeline"""
    initial_state = ResearchAgentState(
        depth=params["depth"],
        breadth=params["breadth"],
        query=params["query"],
        results="",
        directions="",
        learnings="",
        report=""
    )
    
    total_steps = 7 + 6 * params["depth"]
    progress_bar = st.progress(0)
    progress_text = st.empty()
    tabs = st.tabs(["Queries", "Next Direction", "Learnings", "Report"])
    
    prev_state = {"query": "", "directions": "", "learnings": "", "report": ""}
    
    for event_counter, event in enumerate(graph.compile().stream(initial_state), 1):
        progress = min(int(event_counter / total_steps * 100), 100)
        progress_bar.progress(progress)
        progress_text.text(f"Task {event_counter} of {total_steps} completed.")
        
        event_data = event[next(iter(event))]
        for tab, key in zip(tabs, ["query", "directions", "learnings", "report"]):
            if event_data[key] != prev_state[key]:
                tab.markdown(f"**{key.title()}:**\n\n{event_data[key]}")
                prev_state[key] = event_data[key]
        
        time.sleep(0.1)  # Reduced delay for better performance

def main():
    init_session_state()
    render_header()
    params = render_sidebar()
    
    col1, col2 = st.sidebar.columns(2)
    with col1:
        if not st.session_state.state.research_in_progress:
            if st.button("⚙️ Configure AI Settings"):
                st.session_state.state.show_settings = True
    
    with col2:
        if st.button("🚀 Start Research", disabled=st.session_state.state.research_in_progress):
            st.session_state.state.research_in_progress = True
            st.session_state.state.show_settings = False
    
    if st.session_state.state.show_settings and not st.session_state.state.research_in_progress:
        render_settings()
    
    if st.session_state.state.research_in_progress:
        run_research(params)
        st.session_state.state.research_in_progress = False

if __name__ == "__main__":
    main()
