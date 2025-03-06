import yfinance as yf
import pandas as pd

# Define the stock
ticker = "AAPL"
stock = yf.Ticker(ticker)

# Fetch the option expiration dates
expirations = stock.options
print("Available Expirations:", expirations)

# Choose the first expiration date
selected_expiry = expirations[0]  # You can change this to another expiry date

# Get option chain
opt_chain = stock.option_chain(selected_expiry)

# Extract calls and puts
calls = opt_chain.calls
puts = opt_chain.puts

# Save to CSV for further processing
calls.to_csv("calls_data.csv", index=False)
puts.to_csv("puts_data.csv", index=False)

print("Options data saved to calls_data.csv and puts_data.csv!")
