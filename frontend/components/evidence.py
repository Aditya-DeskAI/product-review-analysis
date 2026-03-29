import streamlit as st

def render_evidence(data: dict):
    transparency = data.get("transparency_and_evidence", {})
    
    st.markdown("### 🔍 Transparency & Sources")
    
    st.warning(f"**Uncertainty Indicator:** {transparency.get('uncertainty_indicator', 'None noted.')}")
    st.markdown("---")
    
    st.markdown("#### 🔗 Sources Analyzed")
    sources = transparency.get("sources", [])
    
    if not sources:
        st.write("No specific sources provided.")
        return

    for src in sources:
        with st.expander(f"Source: {src.get('platform')} (Visited: {src.get('timestamp_of_visit')})"):
            st.markdown(f"**URL:** [{src.get('url')}]({src.get('url')})")
            st.markdown("**User Quotes Extracted:**")
            for quote in src.get("raw_quotes", []):
                st.markdown(f"> *\"{quote}\"*")