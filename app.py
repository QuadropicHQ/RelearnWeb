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
import json
from typing import Dict, Any
from dotenv import load_dotenv, set_key
from dataclasses import dataclass
from relearnweb_backend import graph, ResearchAgentState

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
        "About": "This is a research and learning tool for the web. A Joint Effort by Quadropic OSS and Open Source Contributors.",
        "Get Help": "mailto:oss@quadropic.com",
    }
)

@dataclass
class AppState:
    research_in_progress: bool = False
    show_settings: bool = False
    saved_queries: list = None  # Store previous searches
    feedbacks: list = None  # Store user feedback

def init_session_state():
    """Initialize session state variables"""
    if 'state' not in st.session_state:
        st.session_state.state = AppState(saved_queries=[], feedbacks=[])

def render_sidebar() -> Dict[str, Any]:
    """Render sidebar and return research parameters"""
    st.sidebar.header("Research Parameters")

    saved_queries = st.session_state.state.saved_queries
    new_query = st.sidebar.text_input("Enter Research Query", "Quantum Computing breakthroughs")
    selected_query = st.sidebar.selectbox("🔍 Select a Previous Query", [""] + saved_queries, index=0)
    if selected_query:
        new_query = selected_query

    if st.sidebar.button("💾 Save Query"):
        if new_query and new_query not in saved_queries:
            saved_queries.append(new_query)
            st.sidebar.success(f"✅ Query '{new_query}' saved!")

    if saved_queries:
        query_to_delete = st.sidebar.selectbox("🗑️ Delete a Query", saved_queries)
        if st.sidebar.button("❌ Remove Selected Query"):
            saved_queries.remove(query_to_delete)
            st.sidebar.warning(f"🚮 Query '{query_to_delete}' removed.")

    params = {
        "query": new_query,
        "depth": st.sidebar.number_input("Depth", value=1, min_value=0, max_value=10),
        "breadth": st.sidebar.number_input("Breadth", value=3, min_value=1, max_value=10),
    }
    return params

def collect_feedback():
    """Collect user feedback"""
    st.sidebar.subheader("User Feedback")
    feedback = st.sidebar.text_area("Provide your feedback about the research experience")
    if st.sidebar.button("Submit Feedback"):
        st.session_state.state.feedbacks.append(feedback)
        st.sidebar.success("Thank you for your feedback!")



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

        time.sleep(0.1)

def main():
    init_session_state()
    st.title("RelearnWeb")
    st.write("Research and Learn the Web like a Pro. An FOSS Alternative to OpenAI's DeepResearch.")
    st.markdown("[Learn more about Quadropic](https://quadropic.com)")
    params = render_sidebar()
    collect_feedback()
    
    
    if st.button("🚀 Start Research"):
        st.session_state.state.research_in_progress = True
        run_research(params)
        st.session_state.state.research_in_progress = False

if __name__ == "__main__":
    main()
