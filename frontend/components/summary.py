import streamlit as st

def render_summary(data: dict):
    """Renders the text-based summary and Pros/Cons."""
    st.subheader(f"Insights for: {data['product_name'].title()}")
    
    # Render the overall summary
    st.markdown("### 📝 Overall Consensus")
    st.info(data["overall_summary"])

    # Render Pros and Cons side-by-side using columns
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### ✅ Pros")
        if data["pros"]:
            for pro in data["pros"]:
                st.markdown(f"- {pro}")
        else:
            st.write("No major pros found.")

    with col2:
        st.markdown("### ❌ Cons")
        if data["cons"]:
            for con in data["cons"]:
                st.markdown(f"- {con}")
        else:
            st.write("No major cons found.")
            
    st.markdown("---")
    st.caption(f"**Sources Analyzed:** {', '.join(data['platforms_scraped'])}")