import streamlit as st
import requests
from components.summary import render_summary
from components.dashboard import render_dashboard

# --- CONFIGURATION ---
st.set_page_config(
    page_title="Product Insights Agent",
    page_icon="🔍",
    layout="wide"
)

# Define the backend URL (Ensure FastAPI is running on this port)
BACKEND_URL = "http://127.0.0.1:8000/analyze-product"

# --- MAIN UI ---
st.title("🔍 Product Insights AI Agent")
st.markdown("Enter a product, book, or service below. Our AI agent will autonomously browse the internet, read reviews across multiple platforms, and build a comprehensive insight dashboard for you.")

# Search form
with st.form("search_form"):
    product_query = st.text_input("Product Name (e.g., 'Atomic Habits book', 'iPhone 15 pro')")
    submitted = st.form_submit_button("Generate Insights")

# --- ACTION LOGIC ---
if submitted:
    if not product_query.strip():
        st.warning("Please enter a product name first!")
    else:
        # Show a nice loading spinner while the backend agent does its work
        with st.spinner(f"Agent is booting up and browsing the web for '{product_query}'... This usually takes 30-90 seconds."):
            
            try:
                # Send the POST request to our FastAPI backend
                response = requests.post(
                    BACKEND_URL, 
                    json={"product_name": product_query},
                    timeout=180 # 3-minute timeout because web browsing is slow
                )
                
                # Check if the backend threw an error
                if response.status_code != 200:
                    st.error(f"Backend Error: {response.json().get('detail', 'Unknown error')}")
                else:
                    # Success! Grab the JSON data
                    data = response.json()
                    
                    # --- RENDER THE RESULTS ---
                    st.success("Analysis Complete!")
                    
                    # We use Streamlit tabs to organize the view cleanly
                    tab1, tab2 = st.tabs(["📝 Detailed Summary", "📊 Analytics Dashboard"])
                    
                    with tab1:
                        render_summary(data)
                        
                    with tab2:
                        render_dashboard(data)

            except requests.exceptions.ConnectionError:
                st.error("Could not connect to the backend. Is FastAPI running?")
            except requests.exceptions.Timeout:
                st.error("The agent took too long to respond. The request timed out.")