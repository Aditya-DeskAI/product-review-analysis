import streamlit as st

def render_quick_review(data: dict):
    qr = data.get("quick_review", {})
    
    st.markdown("### ⚡ The TL;DR")
    st.success(f"**Verdict:** {qr.get('one_line_verdict', 'N/A')}")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### 👍 Top 3 Positives")
        for pos in qr.get("top_3_positives", []):
            st.markdown(f"- {pos}")
            
    with col2:
        st.markdown("#### 👎 Top 3 Negatives")
        for neg in qr.get("top_3_negatives", []):
            st.markdown(f"- {neg}")

    st.markdown("---")
    
    st.markdown("### 🧭 Decision Intelligence (Rule-Based)")
    for rule in qr.get("decision_indicators", []):
        st.info(f"**IF you value:** {rule.get('if_you_value')} ➡️ **THEN:** {rule.get('then')}")
        
    st.markdown("### 🎭 Persona Recommendations")
    for persona in data.get("decision_intelligence", []):
        st.markdown(f"- **{persona.get('persona')}:** {persona.get('recommendation')}")