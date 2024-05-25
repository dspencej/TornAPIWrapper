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

# Get Torn City API key data
data = taw.get_key_info()

# Print the key info data
print(data)
