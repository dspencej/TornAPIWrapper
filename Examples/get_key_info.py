from TornAPIWrapper import TornApiWrapper

# Initialize the TornApiWrapper with your API key
taw = TornApiWrapper(api_key="1aBcDeFgH2iJkLmN")  # Insert your API key

# Get Torn City API key data
data = taw.get_key_info()

# Print the key info data
print(data)
