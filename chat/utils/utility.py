import re
import hashlib

def hash_query(query: str) -> str:
    return hashlib.sha256(query.encode("utf-8")).hexdigest()

def parse_ai_block(text: str) -> dict:
    # extract ONLY inside <ai> ... </ai>
    ai_inner = re.search(r"<ai>(.*?)</ai>", text, flags=re.DOTALL)
    if not ai_inner:
        return {}

    inner_text = ai_inner.group(1)

    # now get all sub tags
    pattern = r"<(\w+)>(.*?)</\1>"
    matches = re.findall(pattern, inner_text, flags=re.DOTALL)

    return {tag: value.strip() for tag, value in matches}


def extract_sql(text: str) -> str:
    """
    Extracts the SQL query from a string containing ```sql ... ``` fenced block.
    Returns the inner SQL text or None if not found.
    """
    pattern = r"```sql\s*(.*?)\s*```"
    match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return None

def get_history_from_cache(cache,user:str="test",num_hist:int=4)->list:
    user_hist = cache.get(user)
    if not user_hist: return []

    hist = user_hist.get("history")
    if hist and len(hist) >= num_hist: return hist
    if hist: return hist[-num_hist:]
    return []


def set_history_in_cache(cache,hist:str,user:str="test")->None:
    user_hist = cache.get(user)
    if not user_hist:
        cache.set(user,{"history":[hist]})
    elif user_hist and "history" in user_hist:
        user_hist.get('history').append(hist)    
        cache.set(user,user_hist)
    
        
    