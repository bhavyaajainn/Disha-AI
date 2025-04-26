import os
import joblib
import re
from typing import List, Tuple

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
    if not text or not text.strip():
        return False
        
    text = text.lower().strip()
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
   
    if any(safe_query in text for safe_query in SAFE_QUERIES):
        return False
   
    for pattern in EXPLICIT_BIAS_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            return True
   
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        model_path = os.path.join(current_dir, "..", "training", "bias_model.pkl")
        bias_model = joblib.load(model_path)
        
        prediction = bias_model.predict_proba([text])[0]
        return prediction[1] > 0.8
    except Exception as e:
        print(f"Error using bias model: {e}")
        return False