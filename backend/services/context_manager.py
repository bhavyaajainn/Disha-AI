# services/context_manager.py
from datetime import datetime, timedelta
import hashlib
from typing import Dict, List, Any

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
        
        self.context_store[anon_id]['data'].append({
            'timestamp': datetime.now(),
            'context': context_data
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