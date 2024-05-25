from TornAPIWrapper import TornApiWrapper

# Initialize the TornApiWrapper with your API key
taw = TornApiWrapper(api_key="1aBcDeFgH2iJkLmN")  # Insert your API key

# Get Torn City property data for property with ID 752227 and specific selections
data = taw.get_property(752227, selections=["property", "timestamp"])

# Print the property data
print(data)
