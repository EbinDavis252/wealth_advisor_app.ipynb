import streamlit as st
import matplotlib.pyplot as plt
from portfolio_logic import *
import pandas as pd

# ---------- Streamlit Page Setup ----------
st.set_page_config(page_title="GenAI Wealth Advisor", layout="centered", page_icon="💰")

st.markdown("""
    <style>
    .big-font { font-size:28px !important; font-weight:bold; color:#004d99; }
    .metric-box { border:1px solid #e6e6e6; padding:15px; border-radius:10px; background:#f7f9fc; margin-bottom:20px; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='big-font'>💰 GenAI Wealth Advisor</h1>", unsafe_allow_html=True)
st.caption("Smart investment allocation based on your profile & preferences")

# ---------- User Inputs ----------
st.header("👤 Investor Profile")

col1, col2 = st.columns(2)
with col1:
    age = st.slider("Your Age", 18, 80, 30)
    horizon = st.slider("Investment Horizon (Years)", 1, 30, 10)
with col2:
    income = st.number_input("Annual Income (₹)", 0, step=50000, value=1000000)
    tolerance = st.selectbox("Risk Tolerance", ["low", "medium", "high"])

goal = st.selectbox("🎯 Investment Goal", ["wealth_growth", "retirement", "education", "marriage"])
risk_slider = st.slider("🧠 Risk Appetite Tuner", 0, 100, 60, help="0 = Conservative, 100 = Aggressive")

# ---------- On Button Press ----------
if st.button("📊 Generate Personalized Portfolio"):
    profile = {
        'age': age,
        'income': income,
        'goal': goal,
        'investment_horizon': horizon,
        'risk_tolerance': tolerance
    }

    risk_type = determine_risk_score(profile)
    st.markdown(f"### 🧠 Risk Profile: **{risk_type}**")

    data = load_sample_asset_data()
    base_assets = get_asset_universe(risk_type)

    # Modify assets based on slider
    if risk_slider < 33:
        assets = ["Debt", "Gold", "Cash"]
    elif risk_slider < 66:
        assets = list(set(base_assets + ["Equity", "REIT"]))
    else:
        assets = ["Equity", "Crypto", "REIT", "Gold"]

    weights, ret, vol, sharpe = generate_portfolio(data, assets)

    # ---------- Visualization ----------
    st.subheader("📉 Allocation Breakdown")

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.barh(list(weights.keys()), [v * 100 for v in weights.values()], color="#1f77b4")
    ax.set_xlabel("Allocation (%)")
    ax.set_title("Recommended Asset Allocation")
    ax.invert_yaxis()
    st.pyplot(fig)

    # ---------- Metrics ----------
    st.markdown("### 📈 Portfolio Metrics")
    col3, col4, col5 = st.columns(3)
    col3.metric("Expected Return", f"{round(ret * 100, 2)}%")
    col4.metric("Volatility (Risk)", f"{round(vol * 100, 2)}%")
    col5.metric("Sharpe Ratio", round(sharpe, 2))

    # ---------- Explanations ----------
    st.markdown("### 🔍 Personalized Insights")

    insights = []
    if "Crypto" in weights and weights["Crypto"] > 0.15:
        insights.append("🚀 High allocation to **Crypto** indicates an aggressive growth-oriented portfolio. Be ready for volatility.")

    if "Debt" in weights and weights["Debt"] > 0.3:
        insights.append("🛡️ A strong presence of **Debt instruments** shows a conservative or income-focused allocation.")

    if "Gold" in weights and weights["Gold"] > 0.2:
        insights.append("🏅 Diversification through **Gold** suggests a hedge against market uncertainty.")

    if "Equity" in weights and weights["Equity"] > 0.5:
        insights.append("📈 Heavy **Equity exposure** implies long-term growth potential, ideal for wealth creation.")

    if "REIT" in weights:
        insights.append("🏢 Allocation in **REITs** indicates an attempt to balance returns through real estate income.")

    if len(insights) == 0:
        insights.append("🧠 Your portfolio is well-diversified across multiple asset classes.")

    for insight in insights:
        st.markdown(f"- {insight}")
