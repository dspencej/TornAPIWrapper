import time


class Cache:
    def __init__(self, ttl=300):
        """
        Initialize the Cache with a time-to-live (TTL) value.

        :param ttl: Time-to-live in seconds.
        """
        self.ttl = ttl  # Cache time-to-live in seconds
        self.cache = {}

    def get(self, key):
        """
        Retrieve a value from the cache.

        :param key: The key to look up in the cache.
        :return: The cached value or None if not found or expired.
        """
        if key in self.cache:
            entry = self.cache[key]
            if time.time() - entry['time'] < self.ttl:
                return entry['value']
            else:
                del self.cache[key]
        return None

    def set(self, key, value):
        """
        Store a value in the cache.

        :param key: The key under which to store the value.
        :param value: The value to store in the cache.
        """
        self.cache[key] = {'value': value, 'time': time.time()}
