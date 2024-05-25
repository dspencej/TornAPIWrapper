"""
MIT License

Copyright (c) 2023-Present cxdzc, dspencej

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import requests
from typing import Union, List, Dict
import time
from collections import deque
import logging
import os
import json
from .torn_api_error_handler import TornApiErrorHandler
from colorama import Fore, Style


class TornApiWrapper:
    """
    A Python wrapper for the Torn City API (https://www.torn.com/api.html), providing access to Torn City data.
    """

    base_url = "https://api.torn.com"
    request_limit = 100  # Max 100 requests per minute
    request_log_file = "request_log.json"  # File to store request timestamps

    def __init__(self, api_key: str, log_level=logging.INFO):
        """
        Initialize the TornApiWrapper with the provided API key and log level.

        :param api_key: API key used to authenticate API requests.
        :param log_level: Logging level.
        """
        self.api_key = api_key
        self.api_comment = None
        self.api_error_handler = TornApiErrorHandler().api_error_handler
        self.request_times = deque(self._load_request_times())  # Load request times from file

        # Configure logging
        logging.basicConfig(level=log_level, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(log_level)

        self.logger.info(Fore.MAGENTA + "TornApiWrapper initialized with provided API key." + Style.RESET_ALL)

    def _load_request_times(self):
        """
        Load request times from the log file.

        :return: List of request timestamps.
        """
        try:
            if os.path.exists(self.request_log_file):
                with open(self.request_log_file, "r") as file:
                    request_times = json.load(file)
                    self.logger.info(Fore.GREEN + "Loaded request times from file." + Style.RESET_ALL)
                    return request_times
        except (IOError, json.JSONDecodeError) as e:
            self.logger.error(Fore.RED + f"Error loading request times: {e}" + Style.RESET_ALL)
        return []

    def _save_request_times(self):
        """
        Save the current request times to the log file.
        """
        try:
            with open(self.request_log_file, "w") as file:
                json.dump(list(self.request_times), file)
                self.logger.info(Fore.GREEN + "Saved request times to file." + Style.RESET_ALL)
        except IOError as e:
            self.logger.error(Fore.RED + f"Error saving request times: {e}" + Style.RESET_ALL)

    def _check_request_limit(self):
        """
        Check if the number of requests in the last minute exceeds the limit.
        If the limit is exceeded, delay further requests.
        """
        current_time = time.time()
        # Remove requests older than 60 seconds
        while self.request_times and self.request_times[0] < current_time - 60:
            self.request_times.popleft()
        if len(self.request_times) >= self.request_limit:
            self.logger.warning(
                Fore.YELLOW + "Request limit exceeded: 100 requests per minute. Delaying requests..." + Style.RESET_ALL)
            while len(self.request_times) >= self.request_limit:
                time.sleep(1)
                current_time = time.time()
                while self.request_times and self.request_times[0] < current_time - 60:
                    self.request_times.popleft()
        self.logger.debug(
            Fore.GREEN + f"Request limit check passed with {len(self.request_times)} "
                         f"requests in the last minute." + Style.RESET_ALL)
        self._save_request_times()  # Save updated request times

    def _record_request(self):
        """
        Record a new request timestamp.
        """
        self.request_times.append(time.time())
        self.logger.debug(Fore.GREEN + f"Request recorded at {self.request_times[-1]}." + Style.RESET_ALL)
        self._save_request_times()  # Save updated request times

    def api_request(self, endpoint: str, input_id: int = None, selections: List[str] = None, limit: int = None,
                    sort: str = None, stat: str = None, cat: int = None, log: int = None, from_unix: int = None,
                    to_unix: int = None, unix_timestamp: int = None) -> dict:
        """
        Make a request to the Torn City API.

        :param endpoint: API endpoint.
        :param input_id: ID input for endpoint.
        :param selections: List of selections from available fields.
        :param limit: Limit amount of results.
        :param sort: Sort results.
        :param stat: Select a stat to view.
        :param cat: Filter logs based on the Torn log categories.
        :param log: Filter logs based on the Torn log types.
        :param from_unix: UNIX timestamp to filter results, including entries on or after this timestamp.
        :param to_unix: UNIX timestamp to filter results, including entries on or before this timestamp.
        :param unix_timestamp: UNIX timestamp to get specific stat from date.
        :return: Json-encoded data.
        """
        self.logger.info(
            Fore.MAGENTA + f"Making API request to endpoint: {endpoint} with input_id: {input_id}" + Style.RESET_ALL)
        self._check_request_limit()  # Check if request limit is exceeded
        endpoint = f"{endpoint}{'/' + str(input_id) if input_id else ''}"
        params: Dict[str, Union[str, int]] = {"selections": ','.join(selections)} if selections else {}
        params["key"] = self.api_key
        if limit is not None:
            params["limit"] = limit
        if sort is not None:
            params["sort"] = sort
        if stat is not None:
            params["stat"] = stat
        if cat is not None:
            params["cat"] = cat
        if log is not None:
            params["log"] = log
        if from_unix is not None:
            params["from"] = from_unix
        if to_unix is not None:
            params["to"] = to_unix
        if unix_timestamp is not None:
            params["timestamp"] = unix_timestamp
        if self.api_comment is not None:
            params["comment"] = self.api_comment

        self.logger.debug(Fore.GREEN + f"Request params: {params}" + Style.RESET_ALL)
        response = requests.get(f"{self.base_url}{endpoint}", params=params)
        self._record_request()  # Record the request
        self.logger.info(Fore.MAGENTA + f"Received response with status code: {response.status_code}" + Style.RESET_ALL)
        return self.api_error_handler(response)

    def get_user(self, user_id: int = None, selections: List[str] = None, limit: int = None, stat: str = None,
                 cat: int = None, log: int = None, from_unix: int = None, to_unix: int = None,
                 unix_timestamp: int = None) -> dict:
        """
        Get Torn City user data.

        :param user_id: Torn City user ID.
        :param selections: List of selections from available fields.
        :param limit: Limit amount of results.
        :param stat: Select a stat to view.
        :param cat: Filter based on the log categories.
        :param log: Filter based on the log types.
        :param from_unix: UNIX timestamp to filter results, including entries on or after this timestamp.
        :param to_unix: UNIX timestamp to filter results, including entries on or before this timestamp.
        :param unix_timestamp: UNIX timestamp to get specific stat from date.
        :return: Json-encoded Torn City user data.
        """
        self.logger.info(Fore.MAGENTA + f"Fetching user data for user_id: {user_id}" + Style.RESET_ALL)
        return self.api_request("/user", user_id, selections, limit, sort=None, stat=stat, cat=cat, log=log,
                                from_unix=from_unix, to_unix=to_unix, unix_timestamp=unix_timestamp)

    def get_property(self, property_id: int, selections: List[str] = None) -> dict:
        """
        Get Torn City property data.

        :param property_id: Torn City property ID.
        :param selections: List of selections from available fields.
        :return: Json-encoded Torn City property data.
        """
        self.logger.info(Fore.MAGENTA + f"Fetching property data for property_id: {property_id}" + Style.RESET_ALL)
        return self.api_request("/property", property_id, selections)

    def get_faction(self, faction_id: int = None, selections: List[str] = None, limit: int = None, sort: str = None,
                    from_unix: int = None, to_unix: int = None) -> dict:
        """
        Get Torn City faction data.

        :param faction_id: Torn City faction ID.
        :param selections: List of selections from available fields.
        :param limit: Limit amount of results.
        :param sort: Sort results.
        :param from_unix: UNIX timestamps to filter results, including entries on or after this timestamp.
        :param to_unix: UNIX timestamps to filter results, including entries on or before this timestamp.
        :return: Json-encoded Torn City faction data.
        """
        self.logger.info(Fore.MAGENTA + f"Fetching faction data for faction_id: {faction_id}" + Style.RESET_ALL)
        return self.api_request("/faction", faction_id, selections, limit, sort, stat=None, cat=None, log=None,
                                from_unix=from_unix, to_unix=to_unix, unix_timestamp=None)

    def get_company(self, company_id: int = None, selections: List[str] = None, limit: int = None,
                    from_unix: int = None, to_unix: int = None) -> dict:
        """
        Get Torn City company data.

        :param company_id: Torn City company ID.
        :param selections: List of selections from available fields.
        :param limit: Limit amount of results.
        :param from_unix: UNIX timestamps to filter results, including entries on or after this timestamp.
        :param to_unix: UNIX timestamps to filter results, including entries on or before this timestamp.
        :return: Json-encoded Torn City company data.
        """
        self.logger.info(Fore.MAGENTA + f"Fetching company data for company_id: {company_id}" + Style.RESET_ALL)
        return self.api_request("/company", company_id, selections, limit, sort=None, stat=None, cat=None, log=None,
                                from_unix=from_unix, to_unix=to_unix, unix_timestamp=None)

    def get_market(self, item_id: int, selections: List[str] = None) -> dict:
        """
        Get Torn City market data.

        :param item_id: Torn City item ID.
        :param selections: List of selections from available fields.
        :return: Json-encoded Torn City market data.
        """
        self.logger.info(Fore.MAGENTA + f"Fetching market data for item_id: {item_id}" + Style.RESET_ALL)
        return self.api_request("/market", item_id, selections)

    def get_torn(self, torn_id: Union[str, int] = None, selections: List[str] = None) -> dict:
        """
        Get Torn City data.

        :param torn_id: Torn City ID.
        :param selections: List of selections from available fields.
        :return: Json-encoded Torn City data.
        """
        self.logger.info(Fore.MAGENTA + f"Fetching Torn data for torn_id: {torn_id}" + Style.RESET_ALL)
        return self.api_request("/torn", torn_id, selections)

    def get_key_info(self) -> dict:
        """
        Get Torn City API key data.

        :return: Json-encoded Torn City data.
        """
        self.logger.info(Fore.MAGENTA + "Fetching API key information" + Style.RESET_ALL)
        return self.api_request("/key", None, ["info"])
