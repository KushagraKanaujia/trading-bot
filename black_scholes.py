import numpy as np
import pandas as pd
from scipy.stats import norm

# Black-Scholes formula
def black_scholes(S, K, T, r, sigma, option_type="call"):
    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    
    if option_type == "call":
        price = S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
    else:
        price = K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
    
    return price

# Load options data
calls = pd.read_csv("calls_data.csv")

# Define market parameters
S = 180  # Current stock price (Change based on latest AAPL price)
r = 0.05  # Risk-free rate (5%)
T = 30 / 365  # 30 days to expiration

# Remove invalid implied volatility values
calls = calls.dropna(subset=['impliedVolatility'])

# Calculate Black-Scholes prices for each strike price
calls["bs_price"] = calls.apply(lambda row: black_scholes(S, row["strike"], T, r, row["impliedVolatility"], "call"), axis=1)

# Save updated data
calls.to_csv("calls_with_bs.csv", index=False)

print("✅ Black-Scholes prices calculated and saved to calls_with_bs.csv!")
