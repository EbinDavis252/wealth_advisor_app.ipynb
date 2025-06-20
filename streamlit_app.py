import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
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
    st.success(f"🧠 Risk Profile: **{risk_type}**")

    data = load_sample_asset_data()
    assets = get_asset_universe(risk_type)
    weights, ret, vol, sharpe = generate_portfolio(data, assets)

    st.subheader("📊 Detailed Recommended Portfolio")

    # Create a detailed DataFrame for display
    mu = expected_returns.mean_historical_return(data[assets])
    asset_volatility = data[assets].pct_change().std() * (12 ** 0.5)

    portfolio_df = pd.DataFrame({
        "Asset": list(weights.keys()),
        "Allocation %": [round(w * 100, 2) for w in weights.values()],
        "Expected Return %": [round(mu[asset] * 100, 2) for asset in weights.keys()],
        "Risk (Volatility %)": [round(asset_volatility[asset] * 100, 2) for asset in weights.keys()]
    })

    st.dataframe(portfolio_df, use_container_width=True)

    # Display Portfolio Metrics
    st.subheader("📈 Portfolio Metrics")
    st.metric("Expected Annual Return", f"{round(ret * 100, 2)}%")
    st.metric("Risk (Volatility)", f"{round(vol * 100, 2)}%")
    st.metric("Sharpe Ratio", round(sharpe, 2))

    # 📊 Horizontal Bar Chart for Asset Allocation%
    st.subheader("📉 Allocation Visualization")

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.barh(portfolio_df["Asset"], portfolio_df["Allocation %"], color="skyblue", edgecolor="black")
    ax.set_xlabel("Allocation (%)")
    ax.set_title("Recommended Asset Allocation")
    ax.invert_yaxis()  # Highest allocation on top
    st.pyplot(fig)
