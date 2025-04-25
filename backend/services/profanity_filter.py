# services/profanity_filter.py
import re
import os
from enum import Enum
from typing import Dict, List, Tuple, Optional

class ContentCategory(Enum):
    """Categories for potentially problematic content"""
    PROFANITY = "profanity"
    AGGRESSION = "aggression"
    INAPPROPRIATE = "inappropriate"
    CLEAN = "clean"

class ProfanityFilter:
    """Filter for detecting and handling profanity and inappropriate content"""
    
    def __init__(self, strict_mode: bool = False):
        self.strict_mode = strict_mode
        
        # Load word lists (would be in separate files in real implementation)
        self.profanity_words = self._load_word_list("profanity")
        self.aggressive_words = self._load_word_list("aggression") 
        self.inappropriate_words = self._load_word_list("inappropriate")
        
        # Common euphemisms and obfuscations
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
        
        # Context exceptions (when words that could be profanity are used in legitimate contexts)
        self.context_exceptions = {
            'analysis': [r'in-depth analysis', r'detailed analysis', r'analyze'],
            'document': [r'documentation', r'well-documented'],
            'assessment': [r'skills assessment', r'self-assessment'],
            'assignment': [r'job assignment', r'new assignment']
        }
        
        # Professional redirection responses
        self.redirection_responses = [
            "I'd like to keep our conversation professional and focused on your career goals. How can I help with your professional development?",
            "Let's maintain a professional tone in our conversation. I'm here to help with your career questions and aspirations.",
            "I understand you may be frustrated, but I'd prefer to help you with your professional needs in a constructive way. What career challenges can I assist with?",
            "I'm designed to provide career guidance and support in a professional manner. Could we refocus on your career questions?"
        ]
        
    def _load_word_list(self, list_type: str) -> List[str]:
        """Load word list from file or use default lists"""
        # In actual implementation, would load from files
        # This is a simplified placeholder with minimal examples
        if list_type == "profanity":
            return ["profanity1", "profanity2", "curse", "swear"]
        elif list_type == "aggression":
            return ["idiot", "stupid", "hate", "loser", "destroy"]
        elif list_type == "inappropriate":
            return ["inappropriate1", "inappropriate2"]
        return []
    
    def _check_evasion_patterns(self, text: str) -> bool:
        """Check for attempts to evade profanity filters"""
        lower_text = text.lower()
        for pattern, _ in self.evasion_patterns:
            if re.search(pattern, lower_text):
                return True
        return False
        
    def _check_context_exceptions(self, text: str, word: str) -> bool:
        """Check if word appears in a legitimate context"""
        lower_text = text.lower()
        if word in self.context_exceptions:
            for context in self.context_exceptions[word]:
                if re.search(context, lower_text):
                    return True
        return False
    
    def categorize_content(self, text: str) -> Tuple[ContentCategory, List[str]]:
        """Categorize content based on detected words and patterns"""
        if not text or text.strip() == "":
            return ContentCategory.CLEAN, []
            
        lower_text = text.lower()
        found_words = []
        
        # Check for profanity
        for word in self.profanity_words:
            pattern = r'\b' + re.escape(word) + r'\b'
            if re.search(pattern, lower_text) and not self._check_context_exceptions(lower_text, word):
                found_words.append(word)
                
        if found_words or self._check_evasion_patterns(text):
            return ContentCategory.PROFANITY, found_words
            
        # Check for aggressive language
        for word in self.aggressive_words:
            pattern = r'\b' + re.escape(word) + r'\b'
            if re.search(pattern, lower_text) and not self._check_context_exceptions(lower_text, word):
                found_words.append(word)
                
        if found_words:
            return ContentCategory.AGGRESSION, found_words
            
        # Check for inappropriate content
        for word in self.inappropriate_words:
            pattern = r'\b' + re.escape(word) + r'\b'
            if re.search(pattern, lower_text) and not self._check_context_exceptions(lower_text, word):
                found_words.append(word)
                
        if found_words:
            return ContentCategory.INAPPROPRIATE, found_words
                
        return ContentCategory.CLEAN, []
    
    def filter_text(self, text: str) -> str:
        """Replace profanity with asterisks"""
        if not text:
            return text
            
        result = text
        
        # Check and replace explicit profanity
        for word in self.profanity_words + self.aggressive_words + self.inappropriate_words:
            if len(word) <= 2:  # Skip very short words to avoid false positives
                continue
                
            pattern = r'\b' + re.escape(word) + r'\b'
            replacement = word[0] + '*' * (len(word) - 1)
            result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
            
        # Replace evasion patterns
        for pattern, replacement in self.evasion_patterns:
            result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
            
        return result
    
    def should_redirect(self, text: str) -> bool:
        """Determine if content should be redirected"""
        category, words = self.categorize_content(text)
        
        if self.strict_mode:
            # In strict mode, redirect any non-clean content
            return category != ContentCategory.CLEAN
        else:
            # In regular mode, redirect only profanity
            return category == ContentCategory.PROFANITY
    
    def get_redirection_response(self) -> str:
        """Get a professional redirection response"""
        import random
        return random.choice(self.redirection_responses)
    
    def process_input(self, text: str) -> Tuple[str, bool, Optional[str]]:
        """
        Process input text and determine appropriate action
        
        Returns:
            Tuple containing:
            - Processed text (may be filtered)
            - Boolean indicating if redirection is needed
            - Optional redirection message (if needed)
        """
        category, words = self.categorize_content(text)
        
        if self.should_redirect(text):
            return self.filter_text(text), True, self.get_redirection_response()
            
        # For aggressive content, filter but don't redirect
        if category == ContentCategory.AGGRESSION:
            return self.filter_text(text), False, None
            
        # For clean or mildly inappropriate content, no action needed
        return text, False, None