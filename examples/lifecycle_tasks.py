"""In-memory tasks: no services, credentials, threads, or files are opened."""
events = []

def warm_cache():
    events.append("cache warmed")

def fail_startup():
    events.append("startup failed")
    raise RuntimeError("synthetic startup failure")

def close_database():
    events.append("database closed")
