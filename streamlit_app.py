import streamlit as st
import matplotlib.pyplot as plt
from portfolio_logic import *
import pandas as pd

# --------------- Streamlit Config ----------------
st.set_page_config(page_title="GenAI Wealth Advisor", layout="centered", page_icon="💰")

# --------------- Function for Dynamic Background ----------------
def set_background_by_risk(risk_type):
    color_map = {
        "Conservative": "#e3f2fd",  # light blue
        "Balanced": "#fff8e1",      # soft yellow
        "Aggressive": "#ffebee",    # light pink/red
    }
    gradient = {
        "Conservative": "linear-gradient(to bottom right, #bbdefb, #e3f2fd)",
        "Balanced": "linear-gradient(to bottom right, #fff9c4, #fffde7)",
        "Aggressive": "linear-gradient(to bottom right, #ffcdd2, #ffebee)",
    }

    st.markdown(f"""
        <style>
        .stApp {{
            background: {gradient[risk_type]};
            animation: floatBG 12s ease-in-out infinite alternate;
        }}
        @keyframes floatBG {{
            0% {{ background-position: 0% 50%; }}
            100% {{ background-position: 100% 50%; }}
        }}
        .metric-box {{ background: rgba(255, 255, 255, 0.7); padding:15px; border-radius:12px; }}
        .big-font {{ font-size:28px !important; font-weight:bold; color:#004d99; }}
        </style>
    """, unsafe_allow_html=True)

# --------------- Header Section ----------------
st.markdown("<h1 class='big-font'>💰 GenAI-based Wealth Advisor</h1>", unsafe_allow_html=True)
st.caption("AI-powered personalized investment portfolio engine")

# --------------- Inputs ----------------
st.header("👤 Your Investment Profile")

col1, col2 = st.columns(2)
with col1:
    age = st.slider("Your Age", 18, 80, 30)
    horizon = st.slider("Investment Horizon (Years)", 1, 30, 10)
with col2:
    income = st.number_input("Annual Income (₹)", 0, step=50000, value=1000000)
    tolerance = st.selectbox("Risk Tolerance", ["low", "medium", "high"])

goal = st.selectbox("🎯 Investment Goal", ["wealth_growth", "retirement", "education", "marriage"])
risk_slider = st.slider("🧠 Risk Appetite Tuner", 0, 100, 60, help="0 = Conservative, 100 = Aggressive")

# --------------- Generate Button ----------------
if st.button("📊 Generate Personalized Portfolio"):
    profile = {
        'age': age,
        'income': income,
        'goal': goal,
        'investment_horizon': horizon,
        'risk_tolerance': tolerance
    }

    risk_type = determine_risk_score(profile)
    set_background_by_risk(risk_type)  # Set dynamic background
    st.markdown(f"### 🧠 Risk Profile: **{risk_type}**")

    data = load_sample_asset_data()

    # Adjust asset mix based on slider and profile
    if risk_slider < 33:
        assets = ["Debt", "Gold", "Cash"]
    elif risk_slider < 66:
        assets = ["Equity", "Debt", "Gold", "REIT"]
    else:
        assets = ["Equity", "Crypto", "REIT", "Gold"]

    weights, ret, vol, sharpe = generate_portfolio(data, assets)

    # --------------- Visualization ----------------
    st.subheader("📉 Recommended Asset Allocation")

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.barh(list(weights.keys()), [v * 100 for v in weights.values()], color="#1f77b4")
    ax.set_xlabel("Allocation (%)")
    ax.set_title("Asset Allocation Chart")
    ax.invert_yaxis()
    st.pyplot(fig)

    # --------------- Portfolio Metrics ----------------
    st.markdown("### 📈 Portfolio Performance Metrics")
    col3, col4, col5 = st.columns(3)
    col3.metric("Expected Return", f"{round(ret * 100, 2)}%")
    col4.metric("Volatility (Risk)", f"{round(vol * 100, 2)}%")
    col5.metric("Sharpe Ratio", round(sharpe, 2))

    # --------------- Insights ----------------
    st.markdown("### 🔍 Personalized Insights")

    insights = []
    if "Crypto" in weights and weights["Crypto"] > 0.15:
        insights.append("🚀 High allocation to **Crypto** reflects a bold, high-risk appetite for growth.")
    if "Debt" in weights and weights["Debt"] > 0.3:
        insights.append("🛡️ Heavy **Debt** allocation provides stability and capital protection.")
    if "Gold" in weights and weights["Gold"] > 0.2:
        insights.append("🏅 **Gold** acts as a strong hedge against inflation and volatility.")
    if "Equity" in weights and weights["Equity"] > 0.5:
        insights.append("📈 High **Equity exposure** suggests a focus on long-term capital growth.")
    if "REIT" in weights:
        insights.append("🏢 Allocation to **REITs** provides diversification through real estate-backed income.")

    if len(insights) == 0:
        insights.append("🧠 Your portfolio is well-diversified with balanced risk-return characteristics.")

    for insight in insights:
        st.markdown(f"- {insight}")
