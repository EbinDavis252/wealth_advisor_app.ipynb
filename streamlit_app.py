import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px
from portfolio_logic import *

st.set_page_config(page_title="🤖 GenAI Wealth Advisor", layout="wide")
st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    h1, h2, h3 { color: #2b2b52; }
    .stButton>button {
        background-color: #2b2b52;
        color: white;
        font-weight: bold;
        border-radius: 12px;
    }
    .metric-label { color: #4b4b4b; font-weight: bold; }
    </style>
    <div style='text-align:center;'>
        <img src='https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExbGp5ZHM2b2s0ZW9hMmR3bHhseHlmcnE1czMyaHY4ZGw3bTc3a2NodCZlcD12MV9naWZzX3NlYXJjaCZjdD1n/kH3Zh6hBqydZHyZK8r/giphy.gif' width='120'/>
        <h1>GenAI Wealth Advisor</h1>
        <p><em>Smart investing using AI-powered personalization</em></p>
    </div>
""", unsafe_allow_html=True)

# Sidebar
st.sidebar.header("🧾 Investor Profile")
age = st.sidebar.slider("Age", 18, 100, 30)
income = st.sidebar.number_input("Annual Income (₹)", min_value=0, step=50000, value=1000000)
goal = st.sidebar.selectbox("Goal", ["wealth_growth", "retirement", "education", "marriage"])
horizon = st.sidebar.slider("Investment Horizon (Years)", 1, 30, 10)
tolerance = st.sidebar.radio("Risk Tolerance", ["low", "medium", "high"])

st.sidebar.markdown("""
    <br>
    <small><i>All allocations are AI-optimized based on historical data using PyPortfolioOpt.</i></small>
""")

if st.sidebar.button("🚀 Generate My Portfolio"):
    profile = {
        'age': age,
        'income': income,
        'goal': goal,
        'investment_horizon': horizon,
        'risk_tolerance': tolerance
    }

    risk_type = determine_risk_score(profile)
    st.success(f"🧠 AI-Detected Risk Profile: {risk_type}")

    data = load_sample_asset_data()
    assets = get_asset_universe(risk_type)
    weights, ret, vol, sharpe = generate_portfolio(data, assets)

    mu = expected_returns.mean_historical_return(data[assets])
    vol_data = data[assets].pct_change().std() * (12 ** 0.5)

    portfolio_df = pd.DataFrame({
        "Asset": list(weights.keys()),
        "Allocation (%)": [round(w * 100, 2) for w in weights.values()],
        "Expected Return (%)": [round(mu[a] * 100, 2) for a in weights.keys()],
        "Volatility (%)": [round(vol_data[a] * 100, 2) for a in weights.keys()]
    })

    # Dynamic optimization sliders
    st.markdown("### 🔄 Dynamic Optimization")
    desired_return = st.slider("Desired Expected Return (%)", 0.0, 30.0, float(round(ret*100, 2)), 0.1)
    desired_risk = st.slider("Maximum Acceptable Risk (Volatility %)", 0.0, 40.0, float(round(vol*100, 2)), 0.1)

    # Recompute optimized weights if sliders changed significantly
    if desired_return > ret * 100 or desired_risk < vol * 100:
        ef = EfficientFrontier(mu, risk_models.sample_cov(data[assets]))
        ef.efficient_return(target_return=desired_return/100)
        weights = ef.clean_weights()
        ret, vol, sharpe = ef.portfolio_performance()
        portfolio_df["Allocation (%)"] = [round(weights[a]*100, 2) for a in portfolio_df["Asset"]]

    # Fancy Table
    st.markdown("### 📊 Personalized Portfolio Table")
    st.dataframe(portfolio_df.style
                 .background_gradient(cmap='PuBu', subset=["Allocation (%)"])
                 .format({"Allocation (%)": "{:.2f}", "Expected Return (%)": "{:.2f}", "Volatility (%)": "{:.2f}"}))

    # Portfolio Summary Metrics
    st.markdown("### 📈 Portfolio Performance")
    col1, col2, col3 = st.columns(3)
    col1.metric("Expected Return", f"{round(ret * 100, 2)}%")
    col2.metric("Volatility", f"{round(vol * 100, 2)}%")
    col3.metric("Sharpe Ratio", round(sharpe, 2))

    # Bar Chart for Allocation
    fig = px.bar(portfolio_df, x="Allocation (%)", y="Asset", orientation="h", color="Asset",
                 color_discrete_sequence=px.colors.sequential.RdBu, height=400)
    fig.update_layout(title="Asset Allocation (%)", xaxis_title="%", yaxis_title="Asset")
    st.plotly_chart(fig, use_container_width=True)

    # Explanations
    st.markdown("### 📘 AI Explanation")
    for i, row in portfolio_df.iterrows():
        st.markdown(f"**{row['Asset']}**: {row['Allocation (%)']}% allocation with an expected return of {row['Expected Return (%)']}% and volatility of {row['Volatility (%)']}%.")
        if row['Expected Return (%)'] > 12:
            st.markdown("🔺 This asset offers high growth but comes with higher risk.")
        elif row['Expected Return (%)'] < 6:
            st.markdown("🔻 This is a stable asset aimed at capital preservation.")
        else:
            st.markdown("⚖️ Balanced asset for moderate growth.")

    st.markdown("---")
    st.markdown("""
        <div style='text-align:center;'>
            <img src='https://media.giphy.com/media/QuoVJ2iGQvNeekxjAH/giphy.gif' width='300'/><br>
            <small><i>Powered by GenAI & PyPortfolioOpt for intelligent portfolio design 🚀</i></small>
        </div>
    """, unsafe_allow_html=True)

else:
    st.info("🧠 Enter your profile and click 'Generate My Portfolio' to get started!")
