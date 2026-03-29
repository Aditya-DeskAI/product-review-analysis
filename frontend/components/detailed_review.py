import streamlit as st

def render_detailed_review(data: dict):
    indicators = data.get("detailed_indicators", {})
    
    st.markdown("### 📖 In-Depth 10-Pillar Analysis")
    
    for key, info in indicators.items():
        # Clean up the key name (e.g., "1_overall_verdict" -> "Overall Verdict")
        clean_name = " ".join(key.split("_")[1:]).title()
        
        score = info.get("score_out_of_10", 0)
        color = "green" if score >= 7 else "orange" if score >= 4 else "red"
        
        st.markdown(f"#### {clean_name}")
        st.markdown(f"**Score:** :{color}[{score} / 10]")
        st.write(info.get("commentary", "No commentary provided."))
        st.caption(f"Sentiment: {info.get('positive_percent', 0)}% Positive | {info.get('negative_percent', 0)}% Negative | Impact Weight: {info.get('impact_weight_percent', 0)}%")
        st.divider()