from TornAPIWrapper import TornApiWrapper

# Initialize the TornApiWrapper with your API key
taw = TornApiWrapper(api_key="1aBcDeFgH2iJkLmN")  # Insert your API key

# Get Torn City user data
data = taw.get_user()

# Print the user data
print(data)
