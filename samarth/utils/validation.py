# Query Validation Utility
import re
from typing import Tuple

def validate_query(query: str) -> Tuple[bool, str]:
    """
    Validate SQL query for security and correctness.
    Returns (is_valid, error_message)
    """
    # Check for potentially dangerous keywords
    dangerous_keywords = ["DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "TRUNCATE", "CREATE"]
    
    query_upper = query.upper()
    
    for keyword in dangerous_keywords:
        if keyword in query_upper:
            return False, f"Query contains forbidden operation: {keyword}"
    
    # Check for proper SELECT statement
    if not query_upper.strip().startswith("SELECT"):
        return False, "Query must be a SELECT statement"
    
    # Check for excessive wildcards
    if query.count('*') > 2:
        return False, "Query contains too many wildcard (*) characters"
    
    # Check for proper table references (basic check)
    if "FROM" not in query_upper:
        return False, "Query must specify a FROM clause"
    
    return True, ""

def sanitize_input(input_str: str) -> str:
    """
    Sanitize user input to prevent injection attacks
    """
    # Remove potentially harmful characters
    sanitized = re.sub(r'[;\'"\\]', '', input_str)
    return sanitized.strip()