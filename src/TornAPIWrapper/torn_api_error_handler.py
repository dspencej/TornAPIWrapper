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

import logging
import time
import requests
from typing import Dict
import os


class TornApiError(Exception):
    """Custom exception class for Torn API errors."""

    def __init__(self, error_code: int, error_message: str):
        self.error_code = error_code
        self.error_message = error_message
        super().__init__(f"API Error Code {error_code}: {error_message}")


class TornApiErrorHandler:
    """
    Handle Torn API errors.

    Methods:
    - api_error_handler(response) -> dict: Handle Torn API errors.
    """
    error_codes = {
        0: "Unknown error: Unhandled error, should not occur.",
        1: "Key is empty: Private key is empty in current request.",
        2: "Incorrect Key: Private key is wrong/incorrect format.",
        3: "Wrong type: Requesting an incorrect basic type.",
        4: "Wrong fields: Requesting incorrect selection fields.",
        5: "Too many requests: Requests are blocked for a small period of time because of too many requests per user "
           "(max 100 per minute).",
        6: "Incorrect ID: Wrong ID value.",
        7: "Incorrect ID-entity relation: A requested selection is private (For example, personal data of another "
           "user/faction).",
        8: "IP block: Current IP is banned for a small period of time because of abuse.",
        9: "API disabled: Api system is currently disabled.",
        10: "Key owner is in federal jail: Current key can't be used because owner is in federal jail.",
        11: "Key change error: You can only change your API key once every 60 seconds.",
        12: "Key read error: Error reading key from Database.",
        13: "The key is temporarily disabled due to owner inactivity: The key owner hasn't been online for more than "
            "7 days.",
        14: "Daily read limit reached: Too many records have been pulled today by this user from our cloud services.",
        15: "Temporary error: An error code specifically for testing purposes that has no dedicated meaning.",
        16: "Access level of this key is not high enough: A selection is being called of which this key does not have "
            "permission to access.",
        17: "Backend error occurred, please try again.",
        18: "API key has been paused by the owner."
    }

    def __init__(self, log_level: int = logging.INFO, max_retries: int = 3, retry_delay: float = 1.0):
        # Configure logging
        log_level = os.getenv('TORN_API_LOG_LEVEL', log_level)
        logging.basicConfig(level=int(log_level), format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(int(log_level))

        self.max_retries = max_retries
        self.retry_delay = retry_delay

    def _handle_error(self, error_code: int):
        error_message = self.error_codes.get(error_code, f"Unknown error code {error_code}")
        self.logger.error(f"API Error Code {error_code}: {error_message}")
        raise TornApiError(error_code, error_message)

    def api_error_handler(self, response: requests.Response) -> Dict:
        """
        Handle Torn API errors.

        :param response: Response object from `api_request`.
        :return: Json-encoded data.
        :raises TornApiError: If an API error is encountered.
        """
        self.logger.debug(f"Handling response with status code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            self.logger.debug(f"Response data: {data}")

            if "error" in data:
                error_code = data["error"]["code"]
                self._handle_error(error_code)
            return data
        else:
            self.logger.error(f"HTTP Error {response.status_code}: {response.text}")
            response.raise_for_status()

    def _retry_request(self, request_func, *args, **kwargs):
        attempts = 0
        while attempts < self.max_retries:
            try:
                response = request_func(*args, **kwargs)
                return self.api_error_handler(response)
            except TornApiError as e:
                if e.error_code == 17:  # Temporary error
                    attempts += 1
                    self.logger.warning(f"Temporary error encountered. Retrying {attempts}/{self.max_retries}...")
                    time.sleep(self.retry_delay)
                else:
                    raise
        self.logger.error(f"Max retries reached. Failed to handle request.")
        raise TornApiError(17, "Backend error occurred, please try again.")
