# services/rag_system.py
import os
import json
import hashlib
import time
from typing import Dict, List, Tuple, Optional, Any
import re

class DocumentStore:
    """Simple in-memory document store for career resources and knowledge"""
    
    def __init__(self, data_dir: str = None):
        self.documents = {}
        self.embeddings = {}
        self.data_dir = data_dir or os.path.join(os.path.dirname(__file__), "../data")
        self.load_documents()
        
    def load_documents(self):
        """Load documents from JSON files in data directory"""
        # Load career-specific resources
        resource_files = [
            "community_links.json", 
            "mentorship_links.json",
            # Add more resource files as needed
        ]
        
        for filename in resource_files:
            file_path = os.path.join(self.data_dir, filename)
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r') as f:
                        data = json.load(f)
                        
                    # Process each resource as a separate document
                    for item in data:
                        doc_id = self._generate_id(str(item))
                        
                        # Combine fields into searchable text
                        content = f"{item.get('title', '')} - {item.get('description', '')}"
                        
                        self.documents[doc_id] = {
                            'content': content,
                            'metadata': item,
                            'source': filename.replace('.json', '')
                        }
                except Exception as e:
                    print(f"Error loading {filename}: {e}")
                    
        # Load knowledge base articles (Career FAQs, guides, etc.)
        self._load_knowledge_base()
    
    def _load_knowledge_base(self):
        """Load knowledge base articles"""
        # In production, this would load from a database or CMS
        # For this example, we'll add some hardcoded career knowledge
        
        knowledge_articles = [
            {
                "title": "Resume Best Practices",
                "content": """
                Your resume is your professional snapshot. Keep these tips in mind:
                
                1. Tailor your resume for each job application
                2. Use action verbs and quantify achievements
                3. Keep it concise (1-2 pages)
                4. Include relevant keywords from the job description
                5. Proofread carefully for errors
                6. Use a clean, professional format
                7. Start bullet points with strong action verbs
                8. Focus on achievements rather than responsibilities
                """,
                "tags": ["resume", "application", "job search"]
            },
            {
                "title": "Acing Technical Interviews",
                "content": """
                Technical interviews require specific preparation:
                
                1. Review core concepts in your field
                2. Practice common coding problems
                3. Think aloud during problem-solving
                4. Ask clarifying questions
                5. Test your solution with examples
                6. Consider edge cases
                7. Analyze time and space complexity
                8. Be ready to explain your approach and alternatives
                """,
                "tags": ["interview", "technical", "coding"]
            },
            {
                "title": "Salary Negotiation Strategies",
                "content": """
                Effective salary negotiation can significantly impact your compensation:
                
                1. Research market rates for your role and location
                2. Consider the entire compensation package, not just salary
                3. Let the employer make the first offer
                4. Counter with a specific number slightly higher than your target
                5. Justify your request with your value and experience
                6. Practice your negotiation pitch
                7. Be prepared to discuss benefits and perks
                8. Get the final offer in writing
                """,
                "tags": ["salary", "negotiation", "offer"]
            },
            {
                "title": "Effective Networking Approaches",
                "content": """
                Building a professional network is crucial for career growth:
                
                1. Attend industry events and conferences
                2. Join relevant online communities and forums
                3. Schedule informational interviews
                4. Maintain regular contact with your connections
                5. Offer help before asking for favors
                6. Create a compelling LinkedIn profile
                7. Follow up after meetings and conversations
                8. Join professional associations in your field
                """,
                "tags": ["networking", "connections", "professional"]
            }
        ]
        
        for article in knowledge_articles:
            doc_id = self._generate_id(article["title"])
            self.documents[doc_id] = {
                'content': f"{article['title']}\n\n{article['content']}",
                'metadata': {
                    'title': article['title'],
                    'tags': article['tags']
                },
                'source': 'knowledge_base'
            }
    
    def _generate_id(self, text: str) -> str:
        """Generate a unique ID for a document"""
        return hashlib.md5(text.encode('utf-8')).hexdigest()
    
    def simple_search(self, query: str, top_k: int = 3) -> List[Dict]:
        """
        Simple keyword-based search without vector embeddings
        In a production system, this would use proper embeddings
        """
        query_terms = set(query.lower().split())
        results = []
        
        for doc_id, doc in self.documents.items():
            content = doc['content'].lower()
            metadata = doc.get('metadata', {})
            
            # Calculate simple relevance score
            score = 0
            for term in query_terms:
                if term in content:
                    score += content.count(term)
            
            # Boost score based on metadata matches
            if metadata:
                for key, value in metadata.items():
                    if isinstance(value, str) and any(term in value.lower() for term in query_terms):
                        score += 2
                    elif isinstance(value, list):
                        for item in value:
                            if isinstance(item, str) and any(term in item.lower() for term in query_terms):
                                score += 2
            
            if score > 0:
                results.append({
                    'id': doc_id,
                    'content': doc['content'],
                    'metadata': doc['metadata'],
                    'score': score,
                    'source': doc.get('source', 'unknown')
                })
        
        # Sort by relevance score and return top K
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:top_k]


class RAGSystem:
    """Retrieval Augmented Generation system for Disha AI"""
    
    def __init__(self):
        self.document_store = DocumentStore()
        self.feedback_cache = {}  # For SHAG implementation
        
    def generate_context(self, query: str) -> str:
        """Generate context for the language model based on retrieved documents"""
        results = self.document_store.simple_search(query)
        
        if not results:
            return ""
        
        context_parts = []
        for result in results:
            source = result.get('source', 'knowledge')
            metadata = result.get('metadata', {})
            
            # Format based on source type
            if source == 'community_links' or source == 'mentorship_links':
                context_parts.append(
                    f"RESOURCE: {metadata.get('title', 'Resource')}\n"
                    f"DESCRIPTION: {metadata.get('description', '')}\n"
                    f"URL: {metadata.get('url', '')}\n"
                )
            else:
                context_parts.append(
                    f"KNOWLEDGE: {metadata.get('title', 'Information')}\n"
                    f"{result.get('content', '')}\n"
                )
        
        return "\n".join(context_parts)
    
    def create_augmented_prompt(self, user_query: str) -> str:
        """Create a prompt augmented with relevant context"""
        context = self.generate_context(user_query)
        
        if not context:
            return user_query
        
        # Structured prompt with retrieved context
        return (
            f"User query: {user_query}\n\n"
            f"Here is some relevant information to help craft your response:\n"
            f"{context}\n\n"
            f"Based on this information, please provide a helpful, accurate response to the user's query."
        )
    
    def detect_hallucination(self, response: str) -> bool:
        """
        Detect potential hallucinations in response
        This is a simplified version - production would be more sophisticated
        """
        # Check for markers of uncertainty
        uncertainty_phrases = [
            "I'm not sure", "I don't know", "I think", "probably",
            "might be", "could be", "may be", "possibly", "perhaps",
            "I believe", "as far as I know", "to my knowledge"
        ]
        
        has_uncertainty = any(phrase in response.lower() for phrase in uncertainty_phrases)
        
        # Check for specific claims without sources
        claim_patterns = [
            r"according to research",
            r"studies show",
            r"experts say",
            r"statistics indicate",
            r"it is proven",
            r"research confirms"
        ]
        
        has_unsourced_claims = any(re.search(pattern, response, re.IGNORECASE) for pattern in claim_patterns)
        
        return has_uncertainty or has_unsourced_claims
    
    def collect_feedback(self, query: str, response: str, is_positive: bool) -> None:
        """Collect user feedback for SHAG implementation"""
        feedback_id = hashlib.md5(f"{query}:{response}".encode('utf-8')).hexdigest()
        
        self.feedback_cache[feedback_id] = {
            'query': query,
            'response': response,
            'is_positive': is_positive,
            'timestamp': time.time()
        }
        
        # In production, this would store to a database for training
    
    def self_heal(self, query: str, original_response: str) -> Optional[str]:
        """
        Attempt to self-heal a problematic response
        Returns improved response or None if no improvement needed
        """
        is_hallucination = self.detect_hallucination(original_response)
        
        if not is_hallucination:
            return None
            
        # Get more specific context for self-healing
        context = self.generate_context(query)
        if not context:
            # No additional context available for healing
            # Return a more cautious response
            return (
                "I want to be careful about providing accurate information. "
                "While I don't have specific details about that in my knowledge base, "
                "I can help you find reliable resources or focus on general best practices in this area. "
                "Would you like me to help with that instead?"
            )
        
        # Create a self-healing prompt
        healing_prompt = (
            f"Original query: {query}\n\n"
            f"My previous response may have contained information that wasn't fully supported by my knowledge. "
            f"Here is the most reliable information I have on this topic:\n\n"
            f"{context}\n\n"
            f"Based strictly on this information, I should provide a more accurate response that:"
            f"1. Only includes facts I can verify from the above information"
            f"2. Clearly acknowledges any limitations in my knowledge"
            f"3. Focuses on being helpful while remaining accurate"
            f"4. Avoids speculative claims"
        )
        
        # In a real system, this would pass to the LLM for regeneration
        # For this example, we'll return the healing prompt as placeholder
        return "I need to clarify my previous response based on more accurate information. " + context
    
    def process_query(self, query: str) -> Tuple[str, bool]:
        """
        Process a query using RAG/SHAG techniques
        Returns augmented prompt and whether self-healing was triggered
        """
        augmented_prompt = self.create_augmented_prompt(query)
        needs_healing = False
        
        # This would be expanded in a real implementation
        # to include full healing process after initial response
        
        return augmented_prompt, needs_healing