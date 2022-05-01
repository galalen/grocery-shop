import os
from flask_caching import Cache

cache = Cache(
    config={
        "DEBUG": os.getenv("DEBUG"),
        "CACHE_TYPE": "SimpleCache",
        "CACHE_DEFAULT_TIMEOUT": os.getenv("CACHE_DEFAULT_TIMEOUT", 300),
    }
)
