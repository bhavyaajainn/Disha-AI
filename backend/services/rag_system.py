import os
import json
import hashlib
import time
from typing import Dict, List, Tuple, Optional, Any
import re

class DocumentStore:
  
    def __init__(self, data_dir: str = None):
        self.documents = {}
        self.embeddings = {}
        self.data_dir = data_dir or os.path.join(os.path.dirname(__file__), "../data")
        self.load_documents()
        
    def load_documents(self):
        resource_files = [
            "community_links.json", 
            "mentorship_links.json",
        ]
        
        for filename in resource_files:
            file_path = os.path.join(self.data_dir, filename)
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r') as f:
                        data = json.load(f)
                    for item in data:
                        doc_id = self._generate_id(str(item))

                        content = f"{item.get('title', '')} - {item.get('description', '')}"
                        
                        self.documents[doc_id] = {
                            'content': content,
                            'metadata': item,
                            'source': filename.replace('.json', '')
                        }
                except Exception as e:
                    print(f"Error loading {filename}: {e}")
        self._load_knowledge_base()
    
    def _load_knowledge_base(self):
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
        return hashlib.md5(text.encode('utf-8')).hexdigest()
    
    def simple_search(self, query: str, top_k: int = 3) -> List[Dict]:
        query_terms = set(query.lower().split())
        results = []

        for doc_id, doc in self.documents.items():
            score = self._calculate_relevance_score(doc, query_terms)
            if score > 0:
                results.append({
                    'id': doc_id,
                    'content': doc['content'],
                    'metadata': doc['metadata'],
                    'score': score,
                    'source': doc.get('source', 'unknown')
                })

        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:top_k]

    def _calculate_relevance_score(self, doc: Dict, query_terms: set) -> int:
        content = doc['content'].lower()
        metadata = doc.get('metadata', {})
        score = self._calculate_content_score(content, query_terms)
        score += self._boost_metadata_score(metadata, query_terms)
        return score

    def _calculate_content_score(self, content: str, query_terms: set) -> int:
        return sum(content.count(term) for term in query_terms if term in content)

    def _boost_metadata_score(self, metadata: Dict, query_terms: set) -> int:
        score = 0
        if metadata:
            for key, value in metadata.items():
                score += self._calculate_string_score(value, query_terms)
                score += self._calculate_list_score(value, query_terms)
        return score

    def _calculate_string_score(self, value: Any, query_terms: set) -> int:
        if isinstance(value, str) and any(term in value.lower() for term in query_terms):
            return 2
        return 0

    def _calculate_list_score(self, value: Any, query_terms: set) -> int:
        score = 0
        if isinstance(value, list):
            for item in value:
                if isinstance(item, str) and any(term in item.lower() for term in query_terms):
                    score += 2
        return score


class RAGSystem:
    def __init__(self):
        self.document_store = DocumentStore()
        self.feedback_cache = {}  
        
    def generate_context(self, query: str) -> str:
        results = self.document_store.simple_search(query)
        
        if not results:
            return ""
        
        context_parts = []
        for result in results:
            source = result.get('source', 'knowledge')
            metadata = result.get('metadata', {})
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
        context = self.generate_context(user_query)
        
        if not context:
            return user_query
        return (
            f"User query: {user_query}\n\n"
            f"Here is some relevant information to help craft your response:\n"
            f"{context}\n\n"
            f"Based on this information, please provide a helpful, accurate response to the user's query."
        )
    
    def detect_hallucination(self, response: str) -> bool:
        uncertainty_phrases = [
            "I'm not sure", "I don't know", "I think", "probably",
            "might be", "could be", "may be", "possibly", "perhaps",
            "I believe", "as far as I know", "to my knowledge"
        ]
        
        has_uncertainty = any(phrase in response.lower() for phrase in uncertainty_phrases)
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
        feedback_id = hashlib.md5(f"{query}:{response}".encode('utf-8')).hexdigest()
        
        self.feedback_cache[feedback_id] = {
            'query': query,
            'response': response,
            'is_positive': is_positive,
            'timestamp': time.time()
        }
    
    def self_heal(self, query: str, original_response: str) -> Optional[str]:
        is_hallucination = self.detect_hallucination(original_response)
        
        if not is_hallucination:
            return None
        context = self.generate_context(query)
        if not context:
            return (
                "I want to be careful about providing accurate information. "
                "While I don't have specific details about that in my knowledge base, "
                "I can help you find reliable resources or focus on general best practices in this area. "
                "Would you like me to help with that instead?"
            )
        return "I need to clarify my previous response based on more accurate information. " + context
    
    def process_query(self, query: str) -> Tuple[str, bool]:
        """
        Process a query using RAG/SHAG techniques
        Returns augmented prompt and whether self-healing was triggered
        """
        augmented_prompt = self.create_augmented_prompt(query)
        needs_healing = False
        
        return augmented_prompt, needs_healing