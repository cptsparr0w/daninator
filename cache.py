import json
import os
from datetime import datetime, timedelta

CACHE_DIR = os.path.join(os.getcwd(), "cache") # or your preferred cache path

def get_cached(ticker):
    """
    Returns the full cached structure: 
        {content: {metrics, source, company_info}}
    
    Returns None if:
      - file doesn't exist
      - cache is >1 hour old
      - data structure is invalid
    """
    ticker = ticker.upper()
    cache_file = os.path.join(CACHE_DIR, f"{ticker}.json")
    
    if not os.path.exists(cache_file):
        return None
    
    try:
        with open(cache_file) as f:
            data = json.load(f)
        
        # Ensure proper structure: {timestamp, content: {...}}
        if not isinstance(data, dict):
            print(f"[{ticker}] ⚠️ Cache file malformed (not a dict)")
            os.remove(cache_file)
            return None
        
        if "timestamp" not in data or "content" not in data:
            print(f"[{ticker}] ⚠️ Cache missing required keys")
            os.remove(cache_file)
            return None
        
        content = data["content"]
        if not isinstance(content, dict):
            print(f"[{ticker}] ⚠️ Cache content is not a dict")
            os.remove(cache_file)
            return None
        
        # Check age
        cache_time = datetime.fromisoformat(data["timestamp"])
        if datetime.now() - cache_time >= timedelta(hours=1):
            try:
                os.remove(cache_file)
                print(f"[{ticker}] 🧹 Cache expired and cleared")
            except OSError:
                pass
            return None
        
        # Return full content structure for consistency
        return {"content": content}
    
    except Exception as e:
        print(f"[{ticker}] 🧹 Cache read error: {e}. Clearing cache...")
        try:
            os.remove(cache_file)
        except OSError:
            pass
        return None

def cache_data(ticker, content):
    """
    Caches full structure for 1 hour.
    
    Args:
        ticker (str): stock ticker
        content (dict): must contain keys: metrics, source, company_info
    """
    ticker = ticker.upper()
    os.makedirs(CACHE_DIR, exist_ok=True)
    
    cache_file = os.path.join(CACHE_DIR, f"{ticker}.json")
    
    # Validate content structure
    required_keys = ["metrics", "source", "company_info"]
    missing = [k for k in required_keys if k not in content]
    if missing:
        raise ValueError(f"cache_data() missing required keys: {missing}")
    
    data = {
        "timestamp": datetime.now().isoformat(),
        "content": content
    }
    
    with open(cache_file, 'w') as f:
        json.dump(data, f)
