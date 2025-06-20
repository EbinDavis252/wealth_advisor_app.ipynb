import streamlit as st
from streamlit_lottie import st_lottie
import json
import matplotlib.pyplot as plt
from portfolio_logic import *

# Page Config
st.set_page_config(page_title="GenAI Wealth Advisor", layout="wide")

# Load animation
def load_lottie(path):
    with open(path, "r") as f:
        return json.load(f)

lottie_animation = load_lottie("assets/animation.json")

# Top Section
col1, col2 = st.columns([1, 2])
with col1:
    st_lottie(lottie_animation, height=300, speed=1)
with col2:
    st.title("🧠 GenAI Wealth Advisor")
    st.markdown("""
    Welcome to your AI-powered investment planner. Provide your profile and goals, and we’ll generate an optimal, personalized portfolio using real-time financial modeling.
    """)

st.markdown("---")

# Dynamic Inputs
st.subheader("🎯 Personalize Your Investment Plan")

col1, col2, col3 = st.columns(3)
with col1:
    age = st.slider("Your Age", 18, 70, 30)
with col2:
    income = st.slider("Annual Income (₹)", 200000, 3000000, 1000000, step=50000)
with col3:
    horizon = st.slider("Investment Horizon (Years)", 1, 30, 10)

goal = st.selectbox("Investment Goal 🎓", ["wealth_growth", "retirement", "education", "marriage"])
tolerance = st.select_slider("Risk Tolerance", options=["low", "medium", "high"])

if st.button("🔍 Generate Optimized Portfolio"):
    profile = {
        'age': age,
        'income': income,
        'goal': goal,
        'investment_horizon': horizon,
        'risk_tolerance': tolerance
    }

    risk_type = determine_risk_score(profile)
    st.success(f"🧠 Risk Profile: **{risk_type}**")

    # Portfolio Logic
    data = load_sample_asset_data()
    assets = get_asset_universe(risk_type)
    weights, ret, vol, sharpe = generate_portfolio(data, assets)

    st.subheader("📊 Portfolio Allocation")

    # Horizontal Bar Chart
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.barh(list(weights.keys()), [w * 100 for w in weights.values()], color='teal')
    ax.set_xlabel("Allocation %")
    ax.set_title("Asset Allocation by GenAI Advisor")
    ax.invert_yaxis()
    st.pyplot(fig)

    # Portfolio Metrics
    st.subheader("📈 Portfolio Performance Summary")
    col1, col2, col3 = st.columns(3)
    col1.metric("Expected Return", f"{round(ret * 100, 2)}%")
    col2.metric("Risk (Volatility)", f"{round(vol * 100, 2)}%")
    col3.metric("Sharpe Ratio", f"{round(sharpe, 2)}")

    # 📖 AI-Based Explanation
    st.markdown("### 🤖 Investment Strategy Summary")

    def explain_portfolio(risk_type, weights, ret, vol, sharpe):
        lines = []

        if risk_type == "Conservative":
            lines.append("You're assigned a **Conservative** profile, which emphasizes capital preservation and low volatility.")
        elif risk_type == "Balanced":
            lines.append("Your profile is **Balanced**, targeting a mix of growth and stability.")
        else:
            lines.append("You're classified as **Aggressive**, aiming for high returns with higher risk.")

        major_asset = max(weights, key=weights.get)
        lines.append(f"Your largest allocation is in **{major_asset}**, indicating a strategic tilt.")

        if ret > 0.10:
            lines.append(f"The portfolio is expected to grow at a strong **{round(ret * 100, 2)}% annual return**.")
        else:
            lines.append(f"The expected return is a stable **{round(ret * 100, 2)}% annually**.")

        if vol > 0.15:
            lines.append("Note: Risk is relatively high, which aligns with growth-oriented strategies.")
        elif vol < 0.08:
            lines.append("Risk is well-contained, suitable for preservation-focused goals.")

        if sharpe >= 1:
            lines.append("✅ **Sharpe Ratio is healthy**, meaning returns outweigh the risk.")
        else:
            lines.append("⚠️ Consider revising risk or horizon to improve risk-adjusted return.")

        return "\n\n".join(lines)

    st.markdown(explain_portfolio(risk_type, weights, ret, vol, sharpe))

    st.markdown("---")
    st.markdown("🔄 You can go back and change your inputs anytime to re-optimize your plan.")

