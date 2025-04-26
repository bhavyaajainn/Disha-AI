# services/context_manager.py
from datetime import datetime, timedelta
import hashlib
from typing import Dict, List, Any
import re

class EphemeralContextManager:
    """
    Manages conversational context without storing personally identifiable information.
    All data is ephemeral (temporary) and expires after a configurable time period.
    """
    
    def __init__(self, expiry_hours=24):
        self.context_store = {}
        self.expiry_hours = expiry_hours
        
    def get_anonymous_id(self, session_id, ip_hash):
        """
        Create temporary anonymous ID without storing personally identifiable info.
        Uses a combination of session ID and hashed IP to create a temporary reference
        that can't be traced back to an individual.
        """
        # Use session ID and hashed IP to create temporary reference
        return hashlib.sha256(f"{session_id}:{ip_hash}".encode()).hexdigest()
    
    def scrub_pii(self, text: str) -> str:
        """
        Remove personally identifiable information from text.
        
        This function detects and redacts:
        - Email addresses
        - Phone numbers in various formats
        - Potential identification numbers
        - URLs containing personal identifiers
        """
        if not isinstance(text, str):
            return text
            
        # Email pattern
        text = re.sub(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', '[EMAIL REDACTED]', text)
        
        # Phone number patterns (various formats)
        text = re.sub(r'\b(\+\d{1,3}[\s-]?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}\b', '[PHONE REDACTED]', text)
        
        # Social security / ID number patterns
        text = re.sub(r'\b\d{3}[-\s]?\d{2}[-\s]?\d{4}\b', '[ID REDACTED]', text)
        
        # URLs with potential user IDs
        text = re.sub(r'https?://[^\s/]+/(?:user|profile|account|u)/[a-zA-Z0-9_-]+', '[URL REDACTED]', text)
        
        # Physical addresses (simplified pattern)
        text = re.sub(r'\b\d+\s+[A-Za-z0-9\s,]+(?:Avenue|Ave|Street|St|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr|Way|Court|Ct|Plaza|Square|Sq|Trail|Tr|Parkway|Pkwy|Circle|Cir)\b', '[ADDRESS REDACTED]', text)
        
        # WhatsApp/Telegram number patterns
        text = re.sub(r'\b(?:whatsapp|telegram|signal|viber)(?:\s+at)?\s+[+]?[0-9][0-9\s-]{7,}', '[CONTACT REDACTED]', text)
        
        # LinkedIn profile patterns
        text = re.sub(r'linkedin\.com/in/[a-zA-Z0-9_-]+', '[LINKEDIN REDACTED]', text)
        
        # Other social media handles
        text = re.sub(r'(?:@[a-zA-Z0-9_]{2,})', '[SOCIAL MEDIA HANDLE REDACTED]', text)
        
        return text
        
    def store_context(self, anon_id, context_data):
        """
        Store context with expiration
        
        Args:
            anon_id: Anonymous identifier
            context_data: Dictionary containing contextual data
        """
        if anon_id not in self.context_store:
            self.context_store[anon_id] = {
                'data': [],
                'expires': datetime.now() + timedelta(hours=self.expiry_hours)
            }
        
        # Scrub any PII from the context data
        scrubbed_context = {}
        for key, value in context_data.items():
            if isinstance(value, str):
                scrubbed_context[key] = self.scrub_pii(value)
            else:
                scrubbed_context[key] = value
        
        self.context_store[anon_id]['data'].append({
            'timestamp': datetime.now(),
            'context': scrubbed_context
        })
        
    def get_context(self, anon_id):
        """
        Get stored context if not expired
        
        Args:
            anon_id: Anonymous identifier
            
        Returns:
            List of context data or empty list if no context or expired
        """
        self.cleanup_expired()
        return self.context_store.get(anon_id, {}).get('data', [])
        
    def cleanup_expired(self):
        """Remove expired context data"""
        now = datetime.now()
        expired_keys = [k for k, v in self.context_store.items() 
                        if v['expires'] < now]
        for key in expired_keys:
            del self.context_store[key]