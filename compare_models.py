import pandas as pd
import torch
from train_nn import OptionPriceNN
from sklearn.preprocessing import StandardScaler

# Load data
df = pd.read_csv("calls_with_bs.csv")

# Load trained model
model = OptionPriceNN()
model.load_state_dict(torch.load("option_pricing_nn.pth"))
model.eval()

# Prepare input data
scaler = StandardScaler()
X = scaler.fit_transform(df[["strike", "impliedVolatility"]].values)
X = torch.tensor(X, dtype=torch.float32)

# Get NN predictions
with torch.no_grad():
    df["nn_price"] = model(X).squeeze().numpy()

# Compare NN, Black-Scholes, and Market Prices
df["bs_error"] = abs(df["bs_price"] - df["lastPrice"])
df["nn_error"] = abs(df["nn_price"] - df["lastPrice"])

# Save results
df.to_csv("pricing_comparison.csv", index=False)

print("✅ Pricing comparison saved to pricing_comparison.csv!")
