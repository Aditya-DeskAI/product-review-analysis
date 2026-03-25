import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

def render_dashboard(data: dict):
    """Renders the interactive Plotly charts."""
    st.markdown("### 📊 Review Analytics Dashboard")
    
    col1, col2 = st.columns(2)

    # 1. Gauge Chart for Sentiment Score
    with col1:
        score = data.get("average_sentiment_score", 50)
        
        # Determine color based on score
        color = "green" if score >= 75 else "orange" if score >= 50 else "red"
            
        fig_gauge = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = score,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Average Sentiment Score"},
            gauge = {
                'axis': {'range': [None, 100]},
                'bar': {'color': color},
                'steps': [
                    {'range': [0, 50], 'color': "lightgray"},
                    {'range': [50, 75], 'color': "gray"}
                ]
            }
        ))
        # Make the chart background transparent
        fig_gauge.update_layout(paper_bgcolor="rgba(0,0,0,0)", margin=dict(t=50, b=0, l=0, r=0))
        st.plotly_chart(fig_gauge, use_container_width=True)

    # 2. Bar Chart for Pros vs Cons distribution
    with col2:
        pros_count = len(data.get("pros", []))
        cons_count = len(data.get("cons", []))
        
        df = pd.DataFrame({
            "Category": ["Pros", "Cons"],
            "Count": [pros_count, cons_count]
        })
        
        fig_bar = px.bar(
            df, 
            x="Category", 
            y="Count", 
            color="Category",
            color_discrete_map={"Pros": "#00CC96", "Cons": "#EF553B"},
            title="Volume of Key Insights"
        )
        fig_bar.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_bar, use_container_width=True)