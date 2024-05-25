import time

class Cache:
    def __init__(self, ttl=300):
        self.ttl = ttl  # Cache time-to-live in seconds
        self.cache = {}

    def get(self, key):
        if key in self.cache:
            entry = self.cache[key]
            if time.time() - entry['time'] < self.ttl:
                return entry['value']
            else:
                del self.cache[key]
        return None

    def set(self, key, value):
        self.cache[key] = {'value': value, 'time': time.time()}
