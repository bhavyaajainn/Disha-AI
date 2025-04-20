import os
import joblib
import re
from typing import List, Tuple

# Define explicit bias patterns as a backup/addition to the ML model
EXPLICIT_BIAS_PATTERNS = [
    r"women (are|is) (not|less|worse|weaker|inferior)",
    r"men (are|is) (more|better|stronger|superior)",
    r"girls (can't|cannot|don't|do not) (handle|understand|do|perform)",
    r"females (are|aren't|can't) (as|good|capable)",
    r"too emotional for",
    r"belongs in the kitchen",
    r"women should be",
    r"gender stereotype"
]

def is_gender_biased(text: str) -> bool:
    """
    Improved gender bias detection using a combination of:
    1. Pattern matching for explicit bias
    2. ML model for more subtle bias
    3. Safe lists for common non-biased topics
    """
    # Skip empty text
    if not text or not text.strip():
        return False
        
    text = text.lower().strip()
    
    # SAFE LIST: Common career-related queries that should never be flagged
    SAFE_QUERIES = [
        "behavioral interview",
        "linkedin profile",
        "resume",
        "cv",
        "scholarships for women",
        "women in tech",
        "women coders",
        "mentorship",
        "leadership",
        "career advice",
        "job search",
        "interview prep",
        "prepare for interview"
    ]
    
    # If the query contains safe topics, don't flag it
    if any(safe_query in text for safe_query in SAFE_QUERIES):
        return False
    
    # Check for explicit bias patterns
    for pattern in EXPLICIT_BIAS_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    
    # Use the ML model as a backup for more subtle bias
    # that wasn't caught by the explicit patterns
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        model_path = os.path.join(current_dir, "..", "training", "bias_model.pkl")
        bias_model = joblib.load(model_path)
        
        # Only return True if we're very confident (threshold could be adjusted)
        prediction = bias_model.predict_proba([text])[0]
        # If probability of being biased (class 1) is > 0.8, flag it
        return prediction[1] > 0.8
    except Exception as e:
        print(f"Error using bias model: {e}")
        # Fall back to pattern matching only if model fails
        return False