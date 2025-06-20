import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
from portfolio_logic import *
from pypfopt import EfficientFrontier

st.set_page_config(page_title="GenAI Wealth Advisor", layout="centered")
st.title("💰 GenAI-based Wealth Advisor")
st.markdown("Enter your investment profile to receive a personalized portfolio.")

# User Inputs
age = st.number_input("Your Age", min_value=18, max_value=100, value=30)
income = st.number_input("Annual Income (₹)", min_value=0, step=50000, value=1000000)
goal = st.selectbox("Investment Goal", ["wealth_growth", "retirement", "education", "marriage"])
horizon = st.slider("Investment Horizon (Years)", min_value=1, max_value=30, value=10)
tolerance = st.radio("Risk Tolerance", ["low", "medium", "high"])

opt_mode = st.selectbox("🎯 Optimization Goal", ["Max Sharpe Ratio", "Min Risk", "Target Return"])

target_ret = None
if opt_mode == "Target Return":
    target_ret = st.slider("🎯 Target Expected Return (%)", min_value=2.0, max_value=30.0, step=0.5, value=12.0)

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
    df = data[assets]
    mu = expected_returns.mean_historical_return(df)
    S = risk_models.sample_cov(df)
    ef = EfficientFrontier(mu, S)

    # Dynamic optimization
    try:
        if opt_mode == "Max Sharpe Ratio":
            weights = ef.max_sharpe()
        elif opt_mode == "Min Risk":
            weights = ef.min_volatility()
        elif opt_mode == "Target Return":
            weights = ef.efficient_return(target_ret / 100)
    except Exception as e:
        st.error(f"Optimization Error: {e}")
        st.stop()

    cleaned_weights = ef.clean_weights()
    ret, vol, sharpe = ef.portfolio_performance()

    # Portfolio Table
    asset_volatility = df.pct_change().std() * (12 ** 0.5)
    portfolio_df = pd.DataFrame({
        "Asset": list(cleaned_weights.keys()),
        "Allocation %": [round(w * 100, 2) for w in cleaned_weights.values()],
        "Expected Return %": [round(mu[asset] * 100, 2) for asset in cleaned_weights.keys()],
        "Risk (Volatility %)": [round(asset_volatility[asset] * 100, 2) for asset in cleaned_weights.keys()]
    })

    st.subheader("📊 Recommended Portfolio")
    st.dataframe(portfolio_df, use_container_width=True)

    st.subheader("📈 Portfolio Metrics")
    st.metric("Expected Annual Return", f"{round(ret * 100, 2)}%")
    st.metric("Risk (Volatility)", f"{round(vol * 100, 2)}%")
    st.metric("Sharpe Ratio", round(sharpe, 2))

    # Bar Chart
    st.subheader("📉 Allocation Breakdown")
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.barh(portfolio_df["Asset"], portfolio_df["Allocation %"], color="skyblue", edgecolor="black")
    ax.set_xlabel("Allocation (%)")
    ax.set_title("Recommended Asset Allocation")
    ax.invert_yaxis()
    st.pyplot(fig)

    # Explanations
    st.subheader("🧠 Intelligent Explanation")

    # Simple rules-based explanation generator
    explanation = []

    top_asset = portfolio_df.loc[portfolio_df["Allocation %"].idxmax(), "Asset"]
    if ret > 0.15:
        explanation.append("🚀 This is a high-growth portfolio with a strong focus on return-oriented assets.")
    elif ret < 0.07:
        explanation.append("🛡️ This is a conservative portfolio with emphasis on capital preservation.")

    if vol > 0.20:
        explanation.append("⚠️ The volatility is relatively high, which means you should expect short-term fluctuations.")
    elif vol < 0.10:
        explanation.append("✅ The portfolio is designed to be stable with minimal risk.")

    if top_asset in ["Equity", "Crypto"]:
        explanation.append(f"📈 High allocation to **{top_asset}** indicates a growth-driven strategy.")
    elif top_asset in ["Debt", "Gold", "Cash"]:
        explanation.append(f"💵 Dominant investment in **{top_asset}** suggests safety-focused wealth preservation.")

    explanation.append(f"📌 This strategy aligns with your **{risk_type}** risk profile.")

    for line in explanation:
        st.markdown(line)
