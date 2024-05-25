import os
import logging
import sys
from TornAPIWrapper import TornApiWrapper

# Configure logging
logging.basicConfig(level=logging.INFO)

# Get API key from environment variable
api_key = os.getenv('TORN_API')
if not api_key:
    logging.error("Environment variable TORN_API not set. Please set the TORN_API environment variable.")
    sys.exit(1)

# Initialize the TornApiWrapper with the API key
taw = TornApiWrapper(api_key=api_key)

# Get Torn City company data for company with ID 77455 and specific selections
data = taw.get_company(77455, selections=["lookup"])

# Print the selections data from the company data
print(data["selections"])
