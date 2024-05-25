from TornAPIWrapper import TornApiWrapper

# Initialize the TornApiWrapper with your API key
taw = TornApiWrapper(api_key="1aBcDeFgH2iJkLmN")  # Insert your API key

# Get Torn City market data for item with ID 336
data = taw.get_market(336)

# Print the market data
print(data)
