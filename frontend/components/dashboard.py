import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

def render_dashboard(data: dict):
    st.markdown("### 📊 Analytics & Visualizations")
    
    # Safely extract data
    indicators = data.get("detailed_indicators", {})
    chart_metrics = data.get("chart_metrics", {})
    
    # Prepare DataFrame for Indicator charts
    ind_names = []
    scores = []
    pos_pct = []
    neg_pct = []
    impacts = []
    
    for k, v in indicators.items():
        name = " ".join(k.split("_")[1:]).title()
        ind_names.append(name)
        scores.append(v.get("score_out_of_10", 0))
        pos_pct.append(v.get("positive_percent", 0))
        neg_pct.append(v.get("negative_percent", 0))
        impacts.append(v.get("impact_weight_percent", 0))
        
    df_ind = pd.DataFrame({
        "Indicator": ind_names, "Score": scores, 
        "Positive %": pos_pct, "Negative %": neg_pct, "Impact": impacts
    })

    # Layout: Row 1
    col1, col2 = st.columns(2)
    
    # 1. Gauge Chart (Overall Verdict)
    with col1:
        overall_score = indicators.get("1_overall_verdict", {}).get("score_out_of_10", 0)
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number", value=overall_score, title={'text': "Overall Score (Out of 10)"},
            gauge={'axis': {'range': [0, 10]}, 'bar': {'color': "teal"}}
        ))
        fig_gauge.update_layout(height=300, margin=dict(t=50, b=0))
        st.plotly_chart(fig_gauge, use_container_width=True)

    # 2. Pie Chart (Overall Sentiment)
    with col2:
        pie_data = chart_metrics.get("overall_sentiment_pie", {})
        fig_pie = px.pie(
            names=["Positive", "Neutral", "Negative"],
            values=[pie_data.get("positive_percent",0), pie_data.get("neutral_percent",0), pie_data.get("negative_percent",0)],
            title="Overall Sentiment Distribution",
            color_discrete_sequence=["#00CC96", "#E4E4E4", "#EF553B"]
        )
        fig_pie.update_layout(height=300, margin=dict(t=50, b=0))
        st.plotly_chart(fig_pie, use_container_width=True)

    # Layout: Row 2
    col3, col4 = st.columns(2)
    
    # 3. Radar Chart (Indicator Scores)
    with col3:
        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(
            r=df_ind["Score"], theta=df_ind["Indicator"], fill='toself', name='Score'
        ))
        fig_radar.update_layout(title="Indicator Performance Radar", polar=dict(radialaxis=dict(visible=True, range=[0, 10])), height=400)
        st.plotly_chart(fig_radar, use_container_width=True)

    # 4. Bubble Chart (Impact vs Sentiment)
    with col4:
        fig_bubble = px.scatter(
            df_ind, x="Positive %", y="Negative %", size="Impact", color="Indicator",
            hover_name="Indicator", title="Parameter Impact on Overall Review", size_max=40
        )
        fig_bubble.update_layout(height=400)
        st.plotly_chart(fig_bubble, use_container_width=True)

    st.markdown("---")

    # 5. Double Bar Graph (Positive vs Negative per Indicator)
    fig_double_bar = go.Figure()
    fig_double_bar.add_trace(go.Bar(x=df_ind["Indicator"], y=df_ind["Positive %"], name='Positive %', marker_color='#00CC96'))
    fig_double_bar.add_trace(go.Bar(x=df_ind["Indicator"], y=df_ind["Negative %"], name='Negative %', marker_color='#EF553B'))
    fig_double_bar.update_layout(title="Sentiment Breakdown per Indicator", barmode='group', xaxis_tickangle=-45)
    st.plotly_chart(fig_double_bar, use_container_width=True)

    # Layout: Row 3
    col5, col6 = st.columns(2)

    # 6. Horizontal Bar Graph (Common Issues)
    with col5:
        issues = chart_metrics.get("common_issues_bar", [])
        if issues:
            df_issues = pd.DataFrame(issues)
            fig_hbar = px.bar(
                df_issues, x="mention_percentage", y="issue_type", orientation='h',
                title="Common Issues & Mention Frequency (%)", color_discrete_sequence=["#EF553B"]
            )
            fig_hbar.update_layout(yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig_hbar, use_container_width=True)
        else:
            st.write("No common issues data available.")

    # 7. Line Chart (Historical Trend)
    with col6:
        trend = chart_metrics.get("historical_trend_line", [])
        if trend:
            df_trend = pd.DataFrame(trend)
            fig_line = px.line(
                df_trend, x="time_period", y="approval_score_out_of_10", markers=True,
                title="Historical Trend of Approval"
            )
            fig_line.update_yaxes(range=[0, 10])
            st.plotly_chart(fig_line, use_container_width=True)
        else:
            st.write("No trend data available.")