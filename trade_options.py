import pandas as pd

# Load comparison data
df = pd.read_csv("pricing_comparison.csv")

# Identify mispricings
df["mispricing"] = df["nn_price"] - df["lastPrice"]
df["trade_signal"] = df["mispricing"].apply(lambda x: "BUY" if x > 0.5 else ("SELL" if x < -0.5 else "HOLD"))

# Save trading signals
df.to_csv("trading_signals.csv", index=False)

print("✅ Trading signals generated and saved to trading_signals.csv!")
