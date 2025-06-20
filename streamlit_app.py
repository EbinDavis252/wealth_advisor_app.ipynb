# streamlit_app.py
import streamlit as st
import matplotlib.pyplot as plt
from portfolio_logic import *

st.set_page_config(page_title="GenAI Wealth Advisor", layout="centered")

st.title("💰 GenAI-based Wealth Advisor")

st.markdown("Enter your investment profile to receive a personalized portfolio.")

# User Inputs
age = st.number_input("Your Age", min_value=18, max_value=100, value=30)
income = st.number_input("Annual Income (₹)", min_value=0, step=50000, value=1000000)
goal = st.selectbox("Investment Goal", ["wealth_growth", "retirement", "education", "marriage"])
horizon = st.slider("Investment Horizon (Years)", min_value=1, max_value=30, value=10)
tolerance = st.radio("Risk Tolerance", ["low", "medium", "high"])

if st.button("Generate Portfolio"):
    profile = {
        'age': age,
        'income': income,
        'goal': goal,
        'investment_horizon': horizon,
        'risk_tolerance': tolerance
    }

    risk_type = determine_risk_score(profile)
    st.success(f"Risk Profile: **{risk_type}**")

    data = load_sample_asset_data()
    assets = get_asset_universe(risk_type)
    weights, ret, vol, sharpe = generate_portfolio(data, assets)

    st.subheader("📊 Recommended Portfolio")
    st.write({k: f"{round(v*100, 2)}%" for k, v in weights.items()})

    st.metric("Expected Annual Return", f"{round(ret*100, 2)}%")
    st.metric("Risk (Volatility)", f"{round(vol*100, 2)}%")
    st.metric("Sharpe Ratio", round(sharpe, 2))

    # Pie Chart
    fig, ax = plt.subplots()
    ax.pie(weights.values(), labels=weights.keys(), autopct='%1.1f%%', startangle=90)
    ax.axis('equal')
    st.pyplot(fig)
