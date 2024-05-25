import os
import logging
import sys

from colorama import Style, Fore

from TornAPIWrapper import TornApiWrapper

# Configure logging
logging.basicConfig(level=logging.INFO)

# Get API key from environment variable
api_key = os.getenv('TORN_API')

if not api_key:
    logging.error(Fore.RED + "Environment variable TORN_API not set. "
                             "Please set TORN_API to your API key." + Style.RESET_ALL)
    sys.exit(1)

# Initialize the TornApiWrapper with the API key
taw = TornApiWrapper(api_key=api_key, log_level=logging.DEBUG)

# Get Torn City company data for company with ID 77455 and specific selections
data = taw.get_company(77455, selections=["lookup"])

# Print the selections data from the company data
print(data["selections"])
