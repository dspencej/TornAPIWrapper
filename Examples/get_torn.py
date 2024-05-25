from TornAPIWrapper import TornApiWrapper

# Initialize the TornApiWrapper with your API key
taw = TornApiWrapper(api_key="1aBcDeFgH2iJkLmN")  # Insert your API key

# Get Torn City data with selections
data = taw.get_torn(selections=["items"])

# Print the Torn City data
print(data)
