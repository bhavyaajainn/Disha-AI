# services/profanity_filter.py
import re
import os
from enum import Enum
from typing import Dict, List, Tuple, Optional

class ContentCategory(Enum):
    PROFANITY = "profanity"
    AGGRESSION = "aggression"
    INAPPROPRIATE = "inappropriate"
    CLEAN = "clean"

class ProfanityFilter:
    def __init__(self, strict_mode: bool = False):
        self.strict_mode = strict_mode
        self.profanity_words = self._load_word_list("profanity")
        self.aggressive_words = self._load_word_list("aggression") 
        self.inappropriate_words = self._load_word_list("inappropriate")
        self.evasion_patterns = [
            # Letter substitutions
            (r'[f][\W_]*[u][\W_]*[c][\W_]*[k]', "f***"),
            (r's[\W_]*h[\W_]*[i][\W_]*[t]', "s***"),
            (r'b[\W_]*[i][\W_]*t[\W_]*c[\W_]*h', "b****"),
            (r'd[\W_]*[a][\W_]*m[\W_]*n', "d***"),
            # Common symbols
            (r'f\*+k', "f***"),
            (r's\*+t', "s***"),
            (r'b\*+h', "b***"),
            # Numbers/symbols as letters
            (r'[a][$][$]', "a**"),
            (r'[f][u][c][k]', "f***"),
            (r'[s][h][i][t]', "s***")
        ]
        self.context_exceptions = {
            'analysis': [r'in-depth analysis', r'detailed analysis', r'analyze'],
            'document': [r'documentation', r'well-documented'],
            'assessment': [r'skills assessment', r'self-assessment'],
            'assignment': [r'job assignment', r'new assignment']
        }
        self.redirection_responses = [
            "I'd like to keep our conversation professional and focused on your career goals. How can I help with your professional development?",
            "Let's maintain a professional tone in our conversation. I'm here to help with your career questions and aspirations.",
            "I understand you may be frustrated, but I'd prefer to help you with your professional needs in a constructive way. What career challenges can I assist with?",
            "I'm designed to provide career guidance and support in a professional manner. Could we refocus on your career questions?"
        ]
        
    def _load_word_list(self, list_type: str) -> List[str]:
        if list_type == "profanity":
            return ["profanity1", "profanity2", "curse", "swear"]
        elif list_type == "aggression":
            return ["idiot", "stupid", "hate", "loser", "destroy"]
        elif list_type == "inappropriate":
            return ["inappropriate1", "inappropriate2"]
        return []
    
    def _check_evasion_patterns(self, text: str) -> bool:
        lower_text = text.lower()
        for pattern, _ in self.evasion_patterns:
            if re.search(pattern, lower_text):
                return True
        return False
        
    def _check_context_exceptions(self, text: str, word: str) -> bool:
        lower_text = text.lower()
        if word in self.context_exceptions:
            for context in self.context_exceptions[word]:
                if re.search(context, lower_text):
                    return True
        return False
    
    def categorize_content(self, text: str) -> Tuple[ContentCategory, List[str]]:
        if not text or text.strip() == "":
            return ContentCategory.CLEAN, []

        lower_text = text.lower()
        found_words = []
        if self._check_category(lower_text, self.profanity_words, found_words):
            return ContentCategory.PROFANITY, found_words

        if self._check_category(lower_text, self.aggressive_words, found_words):
            return ContentCategory.AGGRESSION, found_words

        if self._check_category(lower_text, self.inappropriate_words, found_words):
            return ContentCategory.INAPPROPRIATE, found_words

        return ContentCategory.CLEAN, []

    def _check_category(self, text: str, word_list: List[str], found_words: List[str]) -> bool:
        for word in word_list:
            pattern = r'\b' + re.escape(word) + r'\b'
            if re.search(pattern, text) and not self._check_context_exceptions(text, word):
                found_words.append(word)
        return bool(found_words) or self._check_evasion_patterns(text)
    
    def filter_text(self, text: str) -> str:
        if not text:
            return text
            
        result = text
        for word in self.profanity_words + self.aggressive_words + self.inappropriate_words:
            if len(word) <= 2:  
                continue
                
            pattern = r'\b' + re.escape(word) + r'\b'
            replacement = word[0] + '*' * (len(word) - 1)
            result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
        for pattern, replacement in self.evasion_patterns:
            result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
            
        return result
    
    def should_redirect(self, text: str) -> bool:
        category, _ = self.categorize_content(text)
        
        if self.strict_mode:
            return category != ContentCategory.CLEAN
        else:
            return category == ContentCategory.PROFANITY
    
    def get_redirection_response(self) -> str:
        import random
        return random.choice(self.redirection_responses)
    
    def process_input(self, text: str) -> Tuple[str, bool, Optional[str]]:

        category, _ = self.categorize_content(text)
        
        if self.should_redirect(text):
            return self.filter_text(text), True, self.get_redirection_response()
        if category == ContentCategory.AGGRESSION:
            return self.filter_text(text), False, None
        return text, False, None