import os
import streamlit as st
import requests
from components.quick_review import render_quick_review
from components.detailed_review import render_detailed_review
from components.dashboard import render_dashboard
from components.evidence import render_evidence

# --- CONFIGURATION ---
st.set_page_config(
    page_title="Universal Reviewer AI",
    page_icon="🧠",
    layout="wide"
)

# Read the backend URL from environment or default to localhost
BACKEND_URL = os.getenv("BACKEND_API_URL", "http://127.0.0.1:8000/analyze-product")

# --- MAIN UI ---
st.title("🧠 Universal Reviewer AI")
st.markdown("Enter any product, software, book, or concept. The AI will autonomously research the internet using a rigorous 10-pillar analytical framework to build a comprehensive dashboard.")

with st.form("search_form"):
    product_query = st.text_input("What do you want to analyze? (e.g., 'Tesla Model 3', 'React JS', 'Atomic Habits')")
    submitted = st.form_submit_button("Generate Deep Analysis")

if submitted:
    if not product_query.strip():
        st.warning("Please enter an entity to analyze!")
    else:
        # High timeout because the 10-pillar research takes time!
        with st.spinner(f"Agent is executing a deep-dive on '{product_query}'... This will take 1-3 minutes."):
            try:
                response = requests.post(
                    BACKEND_URL, 
                    json={"product_name": product_query},
                    timeout=6000 # 100 Minute Timeout
                )
                
                if response.status_code != 200:
                    st.error(f"Backend Error: {response.json().get('detail', 'Unknown error')}")
                else:
                    data = response.json()
                    st.success(f"Analysis Complete for: **{data.get('entity_name', '').title()}**")
                    
                    # --- RENDER THE TABS ---
                    tab1, tab2, tab3, tab4 = st.tabs([
                        "⚡ Quick Review", 
                        "📊 Analytics Dashboard", 
                        "📖 Deep Dive", 
                        "🔍 Sources & Evidence"
                    ])
                    
                    with tab1:
                        render_quick_review(data)
                    with tab2:
                        render_dashboard(data)
                    with tab3:
                        render_detailed_review(data)
                    with tab4:
                        render_evidence(data)

            except requests.exceptions.ConnectionError:
                st.error("Could not connect to the backend. Is FastAPI running on port 8000?")
            except requests.exceptions.Timeout:
                st.error("The agent took too long to respond. The request timed out.")