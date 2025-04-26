# services/context_manager.py
from datetime import datetime, timedelta
import hashlib
from typing import Dict, List, Any
import re

class EphemeralContextManager:
    
    def __init__(self, expiry_hours=24):
        self.context_store = {}
        self.expiry_hours = expiry_hours
        
    def get_anonymous_id(self, session_id, ip_hash):
        return hashlib.sha256(f"{session_id}:{ip_hash}".encode()).hexdigest()
    
    def scrub_pii(self, text: str) -> str:
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
        text = re.sub(r'\b\d+\s+[A-Za-z0-9\s,]+(?:Ave|St|Rd|Blvd|Ln|Dr|Way|Ct|Sq|Tr|Pkwy|Cir)\b', '[ADDRESS REDACTED]', text)
        
        # WhatsApp/Telegram number patterns
        text = re.sub(r'\b(?:whatsapp|telegram|signal|viber)(?:\s+at)?\s+[+]?\d[\d\s-]{7,}', '[CONTACT REDACTED]', text)
        
        # LinkedIn profile patterns
        text = re.sub(r'linkedin\.com/in/[a-zA-Z0-9_-]+', '[LINKEDIN REDACTED]', text)
        
        # Other social media handles
        text = re.sub(r'@\w{2,}', '[SOCIAL MEDIA HANDLE REDACTED]', text)
        
        return text
        
    def store_context(self, anon_id, context_data):
        if anon_id not in self.context_store:
            self.context_store[anon_id] = {
                'data': [],
                'expires': datetime.now() + timedelta(hours=self.expiry_hours)
            }
        
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
        self.cleanup_expired()
        return self.context_store.get(anon_id, {}).get('data', [])
        
    def cleanup_expired(self):
        now = datetime.now()
        expired_keys = [k for k, v in self.context_store.items() 
                        if v['expires'] < now]
        for key in expired_keys:
            del self.context_store[key]