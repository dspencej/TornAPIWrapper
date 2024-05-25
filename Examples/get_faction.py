from TornAPIWrapper import TornApiWrapper

# Initialize the TornApiWrapper with your API key
taw = TornApiWrapper(api_key="1aBcDeFgH2iJkLmN")  # Insert your API key

# Get Torn City faction data with selections
data = taw.get_faction(selections=["lookup"])

# Print the faction data
print(data)
