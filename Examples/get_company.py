from TornAPIWrapper import TornApiWrapper

# Initialize the TornApiWrapper with your API key
taw = TornApiWrapper(api_key="1aBcDeFgH2iJkLmN")  # Insert your API key

# Get Torn City company data for company with ID 77455 and specific selections
data = taw.get_company(77455, selections=["lookup"])

# Print the selections data from the company data
print(data["selections"])
