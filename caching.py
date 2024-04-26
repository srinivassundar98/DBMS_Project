import sys
from collections import OrderedDict
import sys
import pickle
import os
import time
import hashlib
#86400
class LRUCache:

    def __init__(self, capacity: int):
        self.cache = OrderedDict()
        self.capacity = capacity  # Maximum capacity in bytes
        self.current_size = 0     # Current size of the cache in bytes

    def get_hash(self, query: str):
        """Generate a hash for the given query."""
        return hash(query)

    def get(self, query: str):
        """Retrieve item from cache using a hash of the query."""
        query_hash = self.get_hash(query)
        if query_hash not in self.cache:
            return None
        else:
            # Move the recently accessed item to the end (to mark it as recently used)
            self.cache.move_to_end(query_hash)
            return self.cache[query_hash]

    def set(self, query: str, value: dict):
        """Add/update a key-value pair in the cache using a hash of the query."""
        query_hash = self.get_hash(query)
        item_size = sys.getsizeof(value) + sys.getsizeof(query_hash)
        # If the key already exists, adjust the current size
        if query_hash in self.cache:
            self.current_size -= sys.getsizeof(self.cache[query_hash]) + sys.getsizeof(query_hash)
            # Remove the old value
            self.cache.pop(query_hash)
        
        # Evict least recently used items if the capacity is exceeded
        while self.current_size + item_size > self.capacity:
            popped_hash, popped_value = self.cache.popitem(last=False)
            self.current_size -= sys.getsizeof(popped_value) + sys.getsizeof(popped_hash)
        
        # Insert the new item
        self.cache[query_hash] = value
        self.current_size += item_size

    def delete(self, query: str):
        """Delete item from cache by query hash."""
        query_hash = self.get_hash(query)
        if query_hash in self.cache:
            # Subtract the size of the removed item from the current size
            self.current_size -= sys.getsizeof(self.cache[query_hash]) + sys.getsizeof(query_hash)
            del self.cache[query_hash]

    def reset(self):
        """Reset the cache, clearing all stored data."""
        self.cache.clear()
        self.current_size = 0


class SimpleFileCache:
    def __init__(self, filename='cache.pkl', ttl=45):
        self.filename = filename
        self.ttl = ttl
        self.data = OrderedDict()
        self.load_cache()

    def get_hash(self, query):
        """Generate a hash for the given query string."""
        return hashlib.sha256(query.encode()).hexdigest()

    def load_cache(self):
        if os.path.exists(self.filename):
            with open(self.filename, 'rb') as f:
                self.data = pickle.load(f)
            self.purge_expired()

    def purge_expired(self):
        current_time = time.time()
        expired_keys = [key for key, value in self.data.items() if current_time - value['timestamp'] > self.ttl]
        for key in expired_keys:
            del self.data[key]
        if expired_keys:
            self.save_cache()

    def save_cache(self):
        with open(self.filename, 'wb') as f:
            pickle.dump(self.data, f)

    def set(self, query, value):
        hashed_key = self.get_hash(query)
        self.data[hashed_key] = {'value': value, 'timestamp': time.time()}
        self.save_cache()

    def get(self, query):
        hashed_key = self.get_hash(query)
        if hashed_key in self.data and time.time() - self.data[hashed_key]['timestamp'] <= self.ttl:
            return self.data[hashed_key]['value']
        return None

    def delete(self, query):
        hashed_key = self.get_hash(query)
        if hashed_key in self.data:
            del self.data[hashed_key]
            self.save_cache()

    def reset(self):
        self.data.clear()
        if os.path.exists(self.filename):
            os.remove(self.filename)



class SummaryCache:
    def __init__(self, capacity: int, filepath='summary_cache.pkl'):
        self.cache = OrderedDict()
        self.capacity = capacity  # Maximum capacity in bytes
        self.current_size = 0     # Current size of the cache in bytes
        self.filepath = filepath  # Path to the pickle file for persisting the cache
        self.load_cache()         # Load cache state from disk

    def get_hash(self, query: str):
        """Generate a hash for the given query."""
        return hash(query)

    def get(self, query: str):
        """Retrieve item from cache using a hash of the query."""
        query_hash = self.get_hash(query)
        if query_hash not in self.cache:
            return None
        self.cache.move_to_end(query_hash)
        return self.cache[query_hash]

    def set(self, query: str, value: dict):
        """Add/update a key-value pair in the cache using a hash of the query."""
        query_hash = self.get_hash(query)
        item_size = sys.getsizeof(value) + sys.getsizeof(query_hash)
        if query_hash in self.cache:
            self.current_size -= sys.getsizeof(self.cache[query_hash]) + sys.getsizeof(query_hash)
            self.cache.pop(query_hash)
        
        while self.current_size + item_size > self.capacity:
            popped_hash, popped_value = self.cache.popitem(last=False)
            self.current_size -= sys.getsizeof(popped_value) + sys.getsizeof(popped_hash)
        
        self.cache[query_hash] = value
        self.current_size += item_size
        self.save_cache()  # Save changes to disk

    def delete(self, query: str):
        """Delete item from cache by query hash."""
        query_hash = self.get_hash(query)
        if query_hash in self.cache:
            self.current_size -= sys.getsizeof(self.cache[query_hash]) + sys.getsizeof(query_hash)
            del self.cache[query_hash]
            self.save_cache()

    def reset(self):
        """Reset the cache, clearing all stored data."""
        self.cache.clear()
        self.current_size = 0
        self.save_cache()

    def save_cache(self):
        """Save the current state of the cache to a file."""
        with open(self.filepath, 'wb') as f:
            pickle.dump(self.cache, f)

    def load_cache(self):
        """Load the cache state from a file."""
        try:
            with open(self.filepath, 'rb') as f:
                self.cache = pickle.load(f)
            # Recalculate the current size based on loaded data
            self.current_size = sum(sys.getsizeof(value) + sys.getsizeof(key) for key, value in self.cache.items())
        except (FileNotFoundError, EOFError):
            self.cache = OrderedDict()

