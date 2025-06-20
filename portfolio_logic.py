# portfolio_logic.py
import pandas as pd
import numpy as np
from pypfopt import EfficientFrontier, risk_models, expected_returns

def determine_risk_score(profile):
    age_score = 1 if profile['age'] < 35 else 2 if profile['age'] < 50 else 3
    income_score = 1 if profile['income'] < 500000 else 2 if profile['income'] < 1500000 else 3
    horizon_score = 1 if profile['investment_horizon'] < 3 else 2 if profile['investment_horizon'] < 7 else 3
    tolerance_score = {'low': 1, 'medium': 2, 'high': 3}.get(profile['risk_tolerance'], 2)
    total = age_score + income_score + horizon_score + tolerance_score

    if total <= 5:
        return "Conservative"
    elif total <= 8:
        return "Balanced"
    else:
        return "Aggressive"

def load_sample_asset_data():
    np.random.seed(42)
    dates = pd.date_range(start="2020-01-01", periods=48, freq="M")
    prices = pd.DataFrame({
        "Equity": np.cumprod(1 + np.random.normal(0.01, 0.05, len(dates))),
        "Debt": np.cumprod(1 + np.random.normal(0.005, 0.01, len(dates))),
        "Gold": np.cumprod(1 + np.random.normal(0.007, 0.03, len(dates))),
        "REIT": np.cumprod(1 + np.random.normal(0.008, 0.04, len(dates))),
        "Crypto": np.cumprod(1 + np.random.normal(0.02, 0.10, len(dates))),
        "Cash": np.ones(len(dates))
    }, index=dates)
    return prices

def get_asset_universe(risk_type):
    if risk_type == "Conservative":
        return ["Debt", "Gold", "Cash"]
    elif risk_type == "Balanced":
        return ["Equity", "Debt", "Gold", "REIT"]
    else:
        return ["Equity", "Crypto", "REIT", "Gold"]

def generate_portfolio(prices, assets, method="Maximize Sharpe Ratio"):
    df = prices[assets]
    mu = expected_returns.mean_historical_return(df)
    S = risk_models.sample_cov(df)

    ef = EfficientFrontier(mu, S)

    if method == "Maximize Sharpe Ratio":
        ef.max_sharpe()
    elif method == "Minimize Volatility":
        ef.min_volatility()
    elif method == "Maximize Return":
        ef.max_return()
    else:
        ef.max_sharpe()  # fallback

    cleaned_weights = ef.clean_weights()
    ret, vol, sharpe = ef.portfolio_performance()
    return cleaned_weights, ret, vol, sharpe

    
    weights = ef.max_sharpe()
    cleaned_weights = ef.clean_weights()
    ret, vol, sharpe = ef.portfolio_performance()
    return cleaned_weights, ret, vol, sharpe
